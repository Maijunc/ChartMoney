from models import User, Bill_Category, Bill, Budget, Payment_Method
from sqlalchemy.orm import Session
from sqlalchemy import select, update, desc, func, delete
from datetime import datetime
import schemas
import security  # 导入安全工具模块

"""
本模块主要负责进行对数据库的增删改查
"""


# 用于用户登录时，查看用户名和密码是否正确
# 返回值说明：
#   - 成功：返回用户对象 (User)
#   - 失败：返回 None (用户不存在或密码错误)
def user_login(user: schemas.User, db: Session):
    result = db.execute(select(User).where((User.username == user.username)))
    select_user = result.scalar_one_or_none()

    # 用户不存在
    if select_user is None:
        return None

    # 验证密码
    # 1. 尝试使用 bcrypt 验证（新用户的加密密码）
    try:
        if security.verify_password(user.password, select_user.password):
            return select_user  # 密码正确，返回用户对象
    except Exception:
        # 2. 如果 bcrypt 验证失败（可能是旧的明文密码），尝试明文对比
        if select_user.password == user.password:
            # 明文密码匹配，自动升级为加密密码
            try:
                # 确保明文密码不超过 72 字节（bcrypt 限制）
                plain_password = user.password
                if len(plain_password.encode('utf-8')) > 72:
                    plain_password = plain_password[:72]
                    print(f"[警告] 用户 {user.username} 的密码超过72字节，已截断")

                hashed_password = security.hash_password(plain_password)
                select_user.password = hashed_password
                db.commit()
                db.refresh(select_user)  # 刷新对象
                print(f"[安全升级] 用户 {user.username} 的密码已自动升级为加密存储")
            except Exception as e:
                print(f"[警告] 密码升级失败: {e}")
                print(f"  - 用户名: {user.username}")
                print(f"  - 明文密码长度: {len(user.password)} 字符")
                print(f"  - 明文密码字节数: {len(user.password.encode('utf-8'))} 字节")
                db.rollback()

            return select_user  # 返回用户对象

    # 密码错误
    return None


# 用于用户的注册
# 返回值说明：
#   - 成功：返回新创建的用户对象 (User)
#   - 失败：返回错误代码
#     -1: 用户名已存在
#     -2: 手机号已注册
#     0: 数据库异常
def user_register(user: schemas.User_register, db: Session):
    check = db.execute(select(User).where((User.username == user.username)))
    check = check.scalar_one_or_none()
    if check is not None:
        return -1  # 用户名已存在

    check = db.execute(select(User).where((User.phone == user.phone)))
    check = check.scalar_one_or_none()
    if check is not None:
        return -2  # 该手机号已被注册

    # 创建要添加到数据库中的用户
    # 使用 bcrypt 加密密码
    hashed_password = security.hash_password(user.password)
    new_user = User(username=user.username, phone=user.phone, password=hashed_password)

    # 添加到数据库中并提交事务
    try:
        db.add(new_user)  # 因为new_user是User模型类，所以add直接会将其添加到user表中
        db.commit()
        db.refresh(new_user)  # 刷新对象，获取数据库生成的 id
        return new_user  # 返回新创建的用户对象
    except Exception:
        db.rollback()  # 回滚事务
        return 0


# # 用于创建账单分类
# def category_add(category: schemas.category_add, db: Session):
#     stmt = select(User).where(User.id==category.user_id)
#     user = db.scalar(stmt)
#     # 检查用户id是否存在
#     if user is None:
#         return -1
#
#     stmt = select(Bill_Category).where(
#         (Bill_Category.name == category.name) &
#         (
#             (Bill_Category.user_id == category.user_id)|      # 用户此前创建过同名分类
#             (Bill_Category.is_sys == True)        # 用户尝试创建一个同系统分类同名的分类
#         ) &
#         (Bill_Category.type == category.type)       # 但是允许用户创建两个同名分类，当且仅当这两个分类类型不同时
#     )
#     check = db.scalar(stmt)
#     # 已存在同名的分类（不管是已存在同名的系统预设分类或是用户之前已经创建过同名的分类）
#     if check is not None:
#         return -2
#
#     new_category = Bill_Category(
#         user_id=category.user_id,
#         is_sys=False,
#         name=category.name,
#         type=category.type      # 修改的地方之一，现在分类分为收入分类和支出分类
#     )
#     try:
#         db.add(new_category)
#         db.commit()
#         return 1
#     except Exception:
#         return 0    # 数据库插入失败


# # 用于修改账单分类
# def category_update(category: schemas.category_update, db: Session):
#     stmt = select(User).where(User.id==category.user_id)
#     user = db.scalar(stmt)
#     # 用户不存在
#     if user is None:
#         return -1
#
#     stmt = select(Bill_Category).where(Bill_Category.id==category.category_id)
#     update_category = db.scalar(stmt)
#     # 分类不存在
#     if update_category is None:
#         return -2
#     else:
#         # 用户不能修改系统预设分类
#         if update_category.is_sys == True:
#             return -3
#
#         # 用户无权修改别的用户的分类
#         if update_category.user_id != category.user_id:
#             return  -4
#
#         # 检查修改后的分类名是否和用户已有的分类名重复
#         stmt = select(Bill_Category).where(
#             (Bill_Category.name == category.name) &     # 分类名相同
#             (
#                 (Bill_Category.user_id == category.user_id) |       # 同一个用户创建
#                 (Bill_Category.is_sys == True)      # 或是一个系统预设分类
#             ) &
#             (Bill_Category.type == category.type)       # 而且是同一个类型的消费
#         )
#         check = db.scalar(stmt)
#         if check is not None:
#             return -5
#         else:
#             try:
#                 # 由于之前已经获取过要更新的那个记录，所以这里直接修改
#                 update_category.name=category.name
#                 update_category.type=category.type
#                 db.commit()
#                 db.refresh(update_category)     # 此处最好刷新一下数据库中的记录状态
#                 return 1
#             except Exception:
#                 # 数据库修改失败
#                 return 0


# # 用于删除账单分类
# def category_delete(category: schemas.category_delete, db: Session):
#     stmt = select(Bill_Category).where(Bill_Category.id==category.category_id)
#     delete_category = db.scalar(stmt)
#     # 不存在此分类
#     if delete_category is None:
#         return -1
#     # 不能删除系统预设分类
#     elif delete_category.is_sys is True:
#         return -2
#     # 不能删除别的用户的分类
#     elif delete_category.user_id != category.user_id:
#         return -3
#
#     stmt = select(Bill).where(Bill.category_id==category.category_id)
#     check = db.scalars(stmt).first()
#     # 如果这个分类有账单存在，不能删除
#     if check is not None:
#         return -4
#
#     # 尝试进行删除操作
#     try:
#         db.delete(delete_category)
#         db.commit()
#         return 1
#     except Exception:
#         # 数据库修改失败
#         return 0


# 用于获取账单分类列表
def category_list(type: int, db: Session):
    try:
        # 获取分类(需要使用scalars)
        stmt = select(Bill_Category).where(
            (Bill_Category.type == type)
        )
        sys_category = db.scalars(stmt).all()
    except Exception:
        return 0

    result_list = []
    for category in sys_category:
        result_list.append({
            "category_id": category.id,
            "name": category.name,
            "type": category.type,
            "create_time": category.create_time,
            "update_time": category.update_time
        })

    return result_list


# 用于获取支付方式列表
def payment_method_list(db: Session):
    try:
        stmt = select(Payment_Method)
        methods = db.scalars(stmt).all()
    except Exception:
        return 0

    result_list = []
    for method in methods:
        result_list.append({
            "method_id": method.id,
            "name": method.name,
        })
    return result_list


# 用于创建账单
def bill_add(bill: schemas.bill_add, db: Session):
    stmt = select(User).where(User.id == bill.user_id)
    user = db.scalar(stmt)
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Bill_Category).where(Bill_Category.id == bill.category_id)
    category = db.scalar(stmt)
    # 分类不存在
    if category is None:
        return -2

    stmt = select(Payment_Method).where(Payment_Method.id == bill.method_id)
    method = db.scalar(stmt)
    # 支付方式不存在
    if method is None:
        return -3

    try:
        new_bill = Bill(
            user_id=bill.user_id,
            category_id=bill.category_id,
            method_id=bill.method_id,
            name=bill.name,
            amount=bill.amount,
            remark=bill.remark,
            bill_time=bill.bill_time
        )
        db.add(new_bill)
        db.commit()
        return 1
    except Exception:
        return 0


# 用于修改账单
def bill_update(bill: schemas.bill_update, db: Session):
    stmt = select(User).where(User.id == bill.user_id)
    user = db.scalar(stmt)

    stmt = select(Bill_Category).where(Bill_Category.id == bill.category_id)
    category = db.scalar(stmt)

    stmt = select(Payment_Method).where(Payment_Method.id == bill.method_id)
    method = db.scalar(stmt)

    stmt = select(Bill).where(Bill.id == bill.bill_id)
    target = db.scalar(stmt)

    # 用户不存在
    if user is None:
        return -1
    # 分类不存在
    if category is None:
        return -2
    # 账单不存在
    if target is None:
        return -3
    # 此账单不属于这个用户
    if target.user_id != bill.user_id:
        return -4
    # 没有这个支付手段
    if method is None:
        return -5

    try:
        # 尝试修改数据库
        stmt = update(Bill).where(Bill.id == bill.bill_id).values(
            category_id=bill.category_id,
            method_id=bill.method_id,
            name=bill.name,
            amount=bill.amount,
            remark=bill.remark,
            bill_time=bill.bill_time
        )
        db.execute(stmt)
        db.commit()
        return 1
    except Exception:
        # 数据库出错
        return 0


# 用于删除账单
def bill_delete(bill: schemas.bill_delete, db: Session):
    stmt = select(User).where(User.id == bill.user_id)
    user = db.scalar(stmt)
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Bill).where(Bill.id == bill.bill_id)
    target = db.scalar(stmt)
    # 账单不存在
    if target is None:
        return -2
    # 此账单不属于此用户
    if target.user_id != bill.user_id:
        return -3

    # 尝试删除
    try:
        db.delete(target)
        db.commit()
        return 1
    except Exception:
        return 0


# 用于批量删除账单
def bill_batch_delete(payload: schemas.bill_batch_delete, db: Session):
    # 校验用户存在
    stmt = select(User).where(User.id == payload.user_id)
    user = db.scalar(stmt)
    if user is None:
        return -1

    # 去重并保证有数据
    bill_ids = list(dict.fromkeys(payload.bill_ids))
    if len(bill_ids) == 0:
        return -4  # bill_ids 为空

    # 查询所有目标账单
    stmt = select(Bill).where(Bill.id.in_(bill_ids))
    bills = db.scalars(stmt).all()

    # 有不存在的 id（严格模式：不做部分删除）
    if len(bills) != len(bill_ids):
        return -2

    # 任意账单不属于该用户（严格模式：不做部分删除）
    if any(b.user_id != payload.user_id for b in bills):
        return -3

    # 执行批量删除
    try:
        stmt = delete(Bill).where(Bill.id.in_(bill_ids))
        result = db.execute(stmt)
        db.commit()
        # result.rowcount 在不同 DB 方言可能为 None，这里做兜底
        deleted_count = result.rowcount if result.rowcount is not None else len(bill_ids)
        return deleted_count
    except Exception:
        return 0


# 用于获取账单
def bill_list(user_id: int, the_time: str, page: int, page_size: int, type: int, db: Session):
    # 先将字符串形式的时间转换为datetime形式
    start_time = datetime.strptime(f"{the_time}-01", "%Y-%m-%d")
    if start_time.month == 12:
        end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
    else:
        end_time = start_time.replace(month=start_time.month + 1, day=1)

    # 计算偏移量
    skip = (page - 1) * page_size

    try:
        stmt = select(
            Bill.category_id,
            Bill.id,
            Bill.method_id,
            Bill_Category.name.label("category_name"),
            Payment_Method.name.label("method_name"),
            Bill_Category.type.label("type"),
            Bill.name,
            Bill.amount,
            Bill.remark,
            Bill.bill_time,
            Bill.create_time,
            Bill.update_time
        ).join(
            Bill_Category,
            Bill.category_id == Bill_Category.id).join(
            Payment_Method,
            Payment_Method.id == Bill.method_id
        ).where(
            (Bill.user_id == user_id) &
            (Bill.bill_time >= start_time) &
            (Bill.bill_time < end_time) &
            (Bill_Category.type == type)
        ).order_by(desc(Bill.bill_time)).offset(skip).limit(page_size)
        the_list = db.execute(stmt)
    except Exception:
        return 0

    # 将查询结果转换为列表
    result = []
    for bill in the_list:
        result.append({
            "category_id": bill.category_id,
            "bill_id": bill.id,
            "method_id": bill.method_id,
            "category_name": bill.category_name,
            "method_name": bill.method_name,
            "name": bill.name,
            "amount": bill.amount,
            "remark": bill.remark,
            "type": bill.type,
            "bill_time": bill.bill_time,
            "create_time": bill.create_time,
            "update_time": bill.update_time
        })

    return result


# 用于获取账单记录条数和分页总数
def get_bill_count(user_id: int, the_time: str, page_size: int, type: int, db: Session):
    stmt = select(User.id).where(User.id == user_id)
    check = db.scalar(stmt)
    if check is None:
        return -1

    # 先将字符串形式的时间转换为datetime形式
    start_time = datetime.strptime(f"{the_time}-01", "%Y-%m-%d")
    if start_time.month == 12:
        end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
    else:
        end_time = start_time.replace(month=start_time.month + 1, day=1)

    # 统计符合条件的记录条数
    try:
        stmt = select(func.count(Bill.id)).join(Bill_Category, Bill.category_id == Bill_Category.id).where(
            (Bill.user_id == user_id) &
            (Bill.bill_time >= start_time) &
            (Bill.bill_time < end_time) &
            (Bill_Category.type == type)
        )
        num = db.scalar(stmt)
    except Exception:
        return 0

    # 计算页面的数量
    if num % 15 != 0:
        page_num = (num // page_size) + 1
    else:
        page_num = num // page_size

    return {
        "total": num,
        "page_num": page_num
    }


# 用于添加预算
def budget_add(budget: schemas.budget_add, db: Session):
    # 值输入的有问题
    if budget.is_total == True and budget.category_id != 0:
        return -1
    if budget.is_total == False and budget.category_id == 0:
        return -1

    try:
        # 验证month的输入是否合法，如果合法则一定可以转换成为datetime
        start_time = datetime.strptime(f"{budget.month}-01", "%Y-%m-%d")
    except Exception:
        return -2

    try:
        stmt = select(User).where(User.id == budget.user_id)
        user = db.scalar(stmt)
        # 用户不存在
        if user is None:
            return -3
    except Exception:
        return 0

    if budget.is_total is False:
        try:
            stmt = select(Budget).where(
                (Budget.user_id == budget.user_id) &
                (Budget.month == budget.month) &
                (Budget.is_total == True)
            )
            total_budget = db.scalar(stmt)
            # 用户尚未设置月度总预算，此时不允许设置细分类目的预算
            if total_budget is None:
                return -4
        except Exception:
            return 0

        try:
            stmt = select(Bill_Category).where((Bill_Category.id == budget.category_id))
            category = db.scalar(stmt)
            # 分类不存在
            if category is None:
                return -5
            if category.type == 1:
                return -6
        except Exception:
            return 0

        try:
            stmt = select(Budget).where(
                (Budget.user_id == budget.user_id) &
                (Budget.month == budget.month) &
                (Budget.category_id == budget.category_id)
            )
            check = db.scalar(stmt)
            # 当月已存在同类预算
            if check is not None:
                return -7
        except Exception:
            return 0
    else:
        try:
            stmt = select(Budget).where(
                (Budget.user_id == budget.user_id) &
                (Budget.month == budget.month) &
                (Budget.is_total == True)
            )
            check = db.scalar(stmt)
            # 当月已存在同类预算
            if check is not None:
                return -7
        except Exception:
            return 0

    # 一切校验完成，才允许创建这个预算
    try:
        if budget.is_total == False:
            new_budget = Budget(
                user_id=budget.user_id,
                category_id=budget.category_id,
                is_total=budget.is_total,
                amount=budget.amount,
                month=budget.month
            )
        else:
            new_budget = Budget(
                user_id=budget.user_id,
                is_total=budget.is_total,
                amount=budget.amount,
                month=budget.month
            )
        db.add(new_budget)
        # db.commit()
        return 1
    except Exception:
        # 尝试添加时发生数据库错误
        return 0


# 用于删除预算
def budget_delete(budget: schemas.budget_delete, db: Session):
    stmt = select(User).where(User.id == budget.user_id)
    try:
        user = db.scalar(stmt)
    except Exception:
        return 0
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Budget).where(Budget.id == budget.budget_id)
    try:
        target = db.scalar(stmt)
    except Exception:
        return 0
    # 预算不存在
    if target is None:
        return -2

    # 目标预算不属于此用户
    if target.user_id != user.id:
        return -3

    # 如果是月度总预算，一并删除当月所有分类的预算
    if target.is_total == True:
        try:
            stmt = delete(Budget).where(
                (Budget.user_id == budget.user_id) &
                (Budget.month == target.month) &
                (Budget.is_total == False)
            )
            db.execute(stmt)
        except Exception:
            return 0

    # 对目标记录进行删除
    try:
        db.delete(target)
        return 1
    except Exception:
        return 0


# 用于修改预算（只能修改amount）
def budget_update(budget: schemas.budget_update, db: Session):
    stmt = select(User).where(User.id == budget.user_id)
    try:
        user = db.scalar(stmt)
    except Exception:
        return 0
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Budget).where(Budget.id == budget.budget_id)
    try:
        target = db.scalar(stmt)
    except Exception:
        return 0
    # 预算不存在
    if target is None:
        return -2

    # 该预算不属于此用户
    if target.user_id != budget.user_id:
        return -3

    # 校验完成之后，进行真正修改
    try:
        stmt = update(Budget).where(Budget.id==budget.budget_id).values(
            amount = budget.amount
        )
        db.execute(stmt)
        return 1
    except Exception:
        return 0


# 用于获取某月的预算列表
def budget_list_month(user_id: int, month: str, db: Session):
    stmt = select(User).where(User.id==user_id)
    try:
        user = db.scalar(stmt)
        # 用户不存在
        if user is None:
            return -1
    except Exception:
        return 0

    try:
        # 验证month的输入是否合法，如果合法则一定可以转换成为datetime
        start_time = datetime.strptime(f"{month}-01", "%Y-%m-%d")
    except Exception:
        return -2

    stmt = select(
        Budget.id,
        Budget.category_id,
        Budget.is_total,
        Bill_Category.name.label("name"),
        Budget.amount,
        Budget.month,
        Budget.create_time,
        Budget.update_time
    ).join(Bill_Category, Bill_Category.id==Budget.category_id, isouter=True).where(
        (Budget.user_id == user_id) &
        (Budget.month == month)
    )
    try:
        result_list = db.execute(stmt).all()
    except Exception:
        return 0

    result = []
    for record in result_list:
        if record.is_total==False:
            result.append({
                "id": record.id,
                "category_id": record.category_id,
                "is_total": record.is_total,
                "name": record.name,
                "amount": record.amount,
                "month": record.month,
                "create_time": record.create_time,
                "update_time": record.update_time
            })
        else:
            result.append({
                "id": record.id,
                "category_id": record.category_id,
                "is_total": record.is_total,
                "name": "本月总预算",
                "amount": record.amount,
                "month": record.month,
                "create_time": record.create_time,
                "update_time": record.update_time
            })

    return result