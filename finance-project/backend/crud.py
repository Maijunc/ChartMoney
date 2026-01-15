from models import User, Bill_Category, Bill, Budget
from sqlalchemy.orm import Session
from sqlalchemy import select, update, desc, func
from datetime import datetime
import schemas

"""
本模块主要负责进行对数据库的增删改查
"""

# 用于用户登录时，查看用户名和密码是否正确，正确就会返回True
def user_login(user: schemas.User, db: Session):
    result = db.execute(select(User).where((User.username == user.username)))
    select_user = result.scalar_one_or_none()
    if select_user is not None:
        if select_user.password == user.password:
            return True
        else:
            return False
    else:
        return False


# 用于用户的注册
def user_register(user: schemas.User_register, db: Session):
    check = db.execute(select(User).where((User.username == user.username)))
    check = check.scalar_one_or_none()
    if check is not None:
        return -1   # 用户名已存在

    check = db.execute(select(User).where((User.phone == user.phone)))
    check = check.scalar_one_or_none()
    if check is not None:
        return -2   # 改手机号已被注册

    # 创建要添加到数据库中的用户
    user = User(username=user.username, phone=user.phone, password=user.password)

    # 添加到数据库中并提交事务
    try:
        db.add(user)    # 因为user是User模型类，所以add直接会将其添加到user表中
        db.commit()
        return 1
    except Exception:
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


# 用于创建账单
def bill_add(bill: schemas.bill_add, db: Session):
    stmt = select(User).where(User.id==bill.user_id)
    user = db.scalar(stmt)
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Bill_Category).where(Bill_Category.id == bill.category_id)
    category = db.scalar(stmt)
    # 分类不存在
    if category is None:
        return -2

    try:
        new_bill = Bill(
            user_id = bill.user_id,
            category_id = bill.category_id,
            amount = bill.amount,
            remark = bill.remark,
            bill_time = bill.bill_time
        )
        db.add(new_bill)
        db.commit()
        return 1
    except Exception:
        return 0


# 用于修改账单
def bill_update(bill: schemas.bill_update, db: Session):
    stmt = select(User).where(User.id==bill.user_id)
    user = db.scalar(stmt)

    stmt = select(Bill_Category).where(Bill_Category.id==bill.category_id)
    category = db.scalar(stmt)

    stmt = select(Bill).where(Bill.id==bill.bill_id)
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

    try:
        # 尝试修改数据库
        stmt = update(Bill).where(Bill.id==bill.bill_id).values(
            category_id=bill.category_id,
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
    stmt = select(User).where(User.id==bill.user_id)
    user = db.scalar(stmt)
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Bill).where(Bill.id==bill.bill_id)
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
            Bill_Category.name.label("name"),
            Bill_Category.type.label("type"),
            Bill.amount,
            Bill.remark,
            Bill.bill_time,
            Bill.create_time,
            Bill.update_time
        ).join(Bill_Category, Bill.category_id == Bill_Category.id).where(
            (Bill.user_id==user_id)&
            (Bill.bill_time>=start_time)&
            (Bill.bill_time<end_time)&
            (Bill_Category.type==type)
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
        stmt = select(func.count(Bill.id)).join(Bill_Category, Bill.category_id==Bill_Category.id).where(
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
    if budget.is_total==True and budget.category_id is not None:
        return -3

    stmt = select(User).where(User.id==budget.user_id)
    user = db.scalar(stmt)
    # 用户不存在
    if user is None:
        return -1

    if budget.is_total is False:
        try:
            stmt = select(Bill_Category).where((Bill_Category.id==budget.category_id))
            category = db.scalar(stmt)
            # 分类存在，但是此分类不属于该用户
            if category.is_sys==False and category.user_id !=budget.user_id:
                return -2
        except Exception:
            # 如果前端输入的值有问题，比如说is_total是False，但是category_id是空，就会引起这个异常结果
            return -3

    try:
        # 验证month的输入是否合法，如果合法则一定可以转换成为datetime
        start_time = datetime.strptime(f"{budget.month}-01", "%Y-%m-%d")
        if start_time.month == 12:
            end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
        else:
            end_time = start_time.replace(month=start_time.month + 1, day=1)
    except Exception:
        return -4

    try:
        new_budget = Budget(
            user_id = budget.user_id,
            category_id = budget.category_id,
            is_total = budget.is_total,
            amount = budget.amount,
            month = budget.month
        )
        db.add(new_budget)
        db.commit()
        return 1
    except Exception:
        # 尝试添加时发生数据库错误
        return 0