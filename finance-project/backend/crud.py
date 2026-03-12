from models import User, Bill_Category, Bill, Budget, Payment_Method
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func, delete
from datetime import datetime, timedelta
from collections import defaultdict
import schemas
import security  # 导入安全工具模块

"""
本模块主要负责进行对数据库的增删改查
"""


# 用于用户登录时，查看用户名和密码是否正确
async def user_login(user: schemas.User, db: AsyncSession):
    result = await db.execute(select(User).where((User.username == user.username)))
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
                await db.commit()
                await db.refresh(select_user)  # 刷新对象
                print(f"[安全升级] 用户 {user.username} 的密码已自动升级为加密存储")
            except Exception as e:
                print(f"[警告] 密码升级失败: {e}")
                print(f"  - 用户名: {user.username}")
                print(f"  - 明文密码长度: {len(user.password)} 字符")
                print(f"  - 明文密码字节数: {len(user.password.encode('utf-8'))} 字节")
                await db.rollback()

            return select_user  # 返回用户对象

    # 密码错误
    return None


async def get_user_info_by_phone(phone: str, db: AsyncSession):
    result = await db.execute(select(User).where((User.phone == phone)))
    select_user = result.scalar_one_or_none()

    # 用户不存在
    if select_user is None:
        return None

    return select_user


# 用于修改密码（通过手机验证码验证）
async def user_change_password(phone: str, new_password: str, db: AsyncSession):
    # 查找用户
    stmt = select(User).where(User.phone == phone)
    user = await db.scalar(stmt)

    if user is None:
        return -1  # 用户不存在

    # 更新密码
    try:
        hashed_password = security.hash_password(new_password)
        user.password = hashed_password
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        print(f"修改密码失败: {e}")
        await db.rollback()
        return 0


# 用于用户的注册
async def user_register(user: schemas.User_register, db: AsyncSession):
    check = await db.execute(select(User).where((User.username == user.username)))
    check = check.scalar_one_or_none()
    if check is not None:
        return -1  # 用户名已存在

    check = await db.execute(select(User).where((User.phone == user.phone)))
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
        await db.commit()
        await db.refresh(new_user)  # 刷新对象，获取数据库生成的 id
        return new_user  # 返回新创建的用户对象
    except Exception:
        await db.rollback()  # 回滚事务
        return 0


# 用于更新用户信息
async def user_update(user_id: int, user_data: schemas.User_update, db: AsyncSession):
    # 查找用户
    stmt = select(User).where(User.id == user_id)
    user = await db.scalar(stmt)

    if user is None:
        return -1  # 用户不存在

    # 如果要更新手机号，检查手机号是否已被其他用户使用
    if user_data.phone:
        stmt = select(User).where(User.phone == user_data.phone, User.id != user_id)
        existing_user = await db.scalar(stmt)
        if existing_user:
            return -2  # 手机号已被其他用户使用

    # 如果要更新邮箱，检查邮箱是否已被其他用户使用
    if user_data.email:
        stmt = select(User).where(User.email == user_data.email, User.id != user_id)
        existing_user = await db.scalar(stmt)
        if existing_user:
            return -3  # 邮箱已被其他用户使用

    # 更新用户信息
    try:
        if user_data.phone:
            user.phone = user_data.phone
        if user_data.avatar is not None:  # 允许设置为空字符串
            user.avatar = user_data.avatar
        if user_data.nickname is not None:
            user.nickname = user_data.nickname
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.signature is not None:
            user.signature = user_data.signature

        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        print(f"更新用户信息失败: {e}")
        await db.rollback()
        return 0


# 用于获取账单分类列表
async def category_list(type: int, db: AsyncSession):
    try:
        # 获取分类(需要使用scalars)
        stmt = select(Bill_Category).where(
            (Bill_Category.type == type)
        )
        result = await db.scalars(stmt)
        sys_category = result.all()
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
async def payment_method_list(db: AsyncSession):
    try:
        stmt = select(Payment_Method)
        result = await db.scalars(stmt)
        methods = result.all()
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
async def bill_add(bill: schemas.bill_add, db: AsyncSession):
    stmt = select(User).where(User.id == bill.user_id)
    user = await db.scalar(stmt)
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Bill_Category).where(Bill_Category.id == bill.category_id)
    category = await db.scalar(stmt)
    # 分类不存在
    if category is None:
        return -2

    stmt = select(Payment_Method).where(Payment_Method.id == bill.method_id)
    method = await db.scalar(stmt)
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
        await db.commit()
        return 1
    except Exception:
        return 0


# 用于修改账单
async def bill_update(bill: schemas.bill_update, db: AsyncSession):
    stmt = select(User).where(User.id == bill.user_id)
    user = await db.scalar(stmt)

    stmt = select(Bill_Category).where(Bill_Category.id == bill.category_id)
    category = await db.scalar(stmt)

    stmt = select(Payment_Method).where(Payment_Method.id == bill.method_id)
    method = await db.scalar(stmt)

    stmt = select(Bill).where(Bill.id == bill.bill_id)
    target = await db.scalar(stmt)

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
        await db.execute(stmt)
        await db.commit()
        return 1
    except Exception:
        # 数据库出错
        return 0


# 用于删除账单
async def bill_delete(bill: schemas.bill_delete, db: AsyncSession):
    print(f"[DEBUG] 收到删除请求: user_id={bill.user_id}, bill_id={bill.bill_id}")

    stmt = select(User).where(User.id == bill.user_id)
    user = await db.scalar(stmt)
    # 用户不存在
    if user is None:
        print(f"[DEBUG] 用户不存在: user_id={bill.user_id}")
        return -1

    stmt = select(Bill).where(Bill.id == bill.bill_id)
    target = await db.scalar(stmt)
    # 账单不存在
    if target is None:
        print(f"[DEBUG] 账单不存在: bill_id={bill.bill_id}")
        return -2
    # 此账单不属于此用户
    if target.user_id != bill.user_id:
        print(f"[DEBUG] 账单不属于此用户: bill_id={bill.bill_id}, user_id={target.user_id} != {bill.user_id}")
        return -3

    # 尝试删除
    try:
        await db.delete(target)
        await db.commit()
        print(f"[DEBUG] 删除成功: bill_id={bill.bill_id}")
        return 1
    except Exception as e:
        print(f"[DEBUG] 删除失败: {e}")
        await db.rollback()
        return 0


# 用于批量删除账单
async def bill_batch_delete(payload: schemas.bill_batch_delete, db: AsyncSession):
    # 校验用户存在
    stmt = select(User).where(User.id == payload.user_id)
    user = await db.scalar(stmt)
    if user is None:
        return -1

    # 去重并保证有数据
    bill_ids = list(dict.fromkeys(payload.bill_ids))
    if len(bill_ids) == 0:
        return -4  # bill_ids 为空

    # 查询所有目标账单
    stmt = select(Bill).where(Bill.id.in_(bill_ids))
    result = await db.scalars(stmt)
    bills = result.all()

    # 有不存在的 id（严格模式：不做部分删除）
    if len(bills) != len(bill_ids):
        return -2

    # 任意账单不属于该用户（严格模式：不做部分删除）
    if any(b.user_id != payload.user_id for b in bills):
        return -3

    # 执行批量删除
    try:
        stmt = delete(Bill).where(Bill.id.in_(bill_ids))
        result = await db.execute(stmt)
        await db.commit()
        # result.rowcount 在不同 DB 方言可能为 None，这里做兜底
        deleted_count = result.rowcount if result.rowcount is not None else len(bill_ids)
        return deleted_count
    except Exception:
        return 0


# 用于获取账单
async def bill_list(user_id: int, the_time: str, page: int, page_size: int, type: int, db: AsyncSession,
                    date_type: str = None, date_value: str = None, category_name: str = None,
                    payment_method_name: str = None, amount: float = None, name_keyword: str = None,
                    remark_keyword: str = None):
    # 计算偏移量
    skip = (page - 1) * page_size

    try:
        # 构建基础查询
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
            Bill.category_id == Bill_Category.id
        ).join(
            Payment_Method,
            Payment_Method.id == Bill.method_id
        )

        # 添加基础条件
        conditions = [
            (Bill.user_id == user_id),
            (Bill_Category.type == type)
        ]

        # 如果传递了 the_time，添加时间过滤条件
        if the_time:
            start_time = datetime.strptime(f"{the_time}-01", "%Y-%m-%d")
            if start_time.month == 12:
                end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
            else:
                end_time = start_time.replace(month=start_time.month + 1, day=1)

            conditions.extend([
                (Bill.bill_time >= start_time),
                (Bill.bill_time < end_time)
            ])

        # 添加筛选条件
        # 1) 动态日期筛选（优先级高于 the_time）
        if date_type and date_value:
            if date_type == 'day':
                conditions.append(Bill.bill_time == datetime.strptime(date_value, "%Y-%m-%d"))
            elif date_type == 'month':
                conditions.append(Bill.bill_time.like(f"{date_value}%"))
            elif date_type == 'year':
                conditions.append(Bill.bill_time.like(f"{date_value}%"))

        # 2) 分类名称筛选
        if category_name:
            conditions.append(Bill_Category.name == category_name)

        # 3) 支付方式筛选
        if payment_method_name:
            conditions.append(Payment_Method.name == payment_method_name)

        # 4) 金额筛选
        if amount is not None:
            conditions.append(Bill.amount == amount)

        # 5) 名称关键字筛选
        if name_keyword:
            conditions.append(Bill.name.like(f"%{name_keyword}%"))

        # 6) 备注关键字筛选
        if remark_keyword:
            conditions.append(Bill.remark.like(f"%{remark_keyword}%"))

        # 应用所有条件
        stmt = stmt.where(*conditions).order_by(desc(Bill.bill_time)).offset(skip).limit(page_size)
        the_list = await db.execute(stmt)
    except Exception:
        return 0

    # 将查询结果转换为列表
    result = []
    for bill in the_list:
        result.append({
            "category_id": bill.category_id,
            "id": bill.id,  # 注意：前端期望的是 id，不是 bill_id
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
async def get_bill_count(user_id: int, the_time: str, page_size: int, type: int, db: AsyncSession,
                        date_type: str = None, date_value: str = None, category_name: str = None,
                        payment_method_name: str = None, amount: float = None, name_keyword: str = None,
                        remark_keyword: str = None):
    stmt = select(User.id).where(User.id == user_id)
    check = await db.scalar(stmt)
    if check is None:
        return -1

    # 统计符合条件的记录条数
    try:
        # 构建基础查询
        stmt = select(func.count(Bill.id)).join(
            Bill_Category,
            Bill.category_id == Bill_Category.id
        ).join(
            Payment_Method,
            Payment_Method.id == Bill.method_id
        )

        # 添加基础条件
        conditions = [
            (Bill.user_id == user_id),
            (Bill_Category.type == type)
        ]

        # 如果传递了 the_time，添加时间过滤条件
        if the_time:
            start_time = datetime.strptime(f"{the_time}-01", "%Y-%m-%d")
            if start_time.month == 12:
                end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
            else:
                end_time = start_time.replace(month=start_time.month + 1, day=1)

            conditions.extend([
                (Bill.bill_time >= start_time),
                (Bill.bill_time < end_time)
            ])

        # 添加筛选条件（与 bill_list 保持一致）
        # 1) 动态日期筛选（优先级高于 the_time）
        if date_type and date_value:
            if date_type == 'day':
                conditions.append(Bill.bill_time == datetime.strptime(date_value, "%Y-%m-%d"))
            elif date_type == 'month':
                conditions.append(Bill.bill_time.like(f"{date_value}%"))
            elif date_type == 'year':
                conditions.append(Bill.bill_time.like(f"{date_value}%"))

        # 2) 分类名称筛选
        if category_name:
            conditions.append(Bill_Category.name == category_name)

        # 3) 支付方式筛选
        if payment_method_name:
            conditions.append(Payment_Method.name == payment_method_name)

        # 4) 金额筛选
        if amount is not None:
            conditions.append(Bill.amount == amount)

        # 5) 名称关键字筛选
        if name_keyword:
            conditions.append(Bill.name.like(f"%{name_keyword}%"))

        # 6) 备注关键字筛选
        if remark_keyword:
            conditions.append(Bill.remark.like(f"%{remark_keyword}%"))

        # 应用所有条件
        stmt = stmt.where(*conditions)
        num = await db.scalar(stmt)
    except Exception:
        return 0

    # 计算页面的数量
    if num % page_size != 0:
        page_num = (num // page_size) + 1
    else:
        page_num = num // page_size

    return {
        "total": num,
        "page_num": page_num
    }


# 用于首页获取统计数据
async def bill_list_first(user_id: int, the_time: str, type: int, db: AsyncSession):
    stmt = select(User.id).where(User.id == user_id)
    check = await db.scalar(stmt)
    if check is None:
        return -1

    try:
        # 构建基础查询
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
            Bill.category_id == Bill_Category.id
        ).join(
            Payment_Method,
            Payment_Method.id == Bill.method_id
        )

        # 添加基础条件
        conditions = [
            (Bill.user_id == user_id),
            (Bill_Category.type == type)
        ]

        # 如果传递了 the_time，添加时间过滤条件
        if the_time:
            start_time = datetime.strptime(f"{the_time}-01", "%Y-%m-%d")
            if start_time.month == 12:
                end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
            else:
                end_time = start_time.replace(month=start_time.month + 1, day=1)

            conditions.extend([
                (Bill.bill_time >= start_time),
                (Bill.bill_time < end_time)
            ])

        # 应用所有条件
        stmt = stmt.where(*conditions).order_by(desc(Bill.bill_time))
        the_list = await db.execute(stmt)
    except Exception:
        return 0

    # 将查询结果转换为列表
    result = []
    for bill in the_list:
        result.append({
            "category_id": bill.category_id,
            "id": bill.id,  # 注意：前端期望的是 id，不是 bill_id
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

# 用于添加预算
async def budget_add(budget: schemas.budget_add, db: AsyncSession):
    # 修复：值输入验证（使用None而不是0）
    if budget.is_total == True and budget.category_id is not None:
        return -1  # 总预算时category_id必须为None
    if budget.is_total == False and budget.category_id is None:
        return -1  # 分类预算时category_id不能为None

    try:
        # 验证month的输入是否合法，如果合法则一定可以转换成为datetime
        start_time = datetime.strptime(f"{budget.month}-01", "%Y-%m-%d")
    except Exception:
        return -2

    try:
        stmt = select(User).where(User.id == budget.user_id)
        user = await db.scalar(stmt)
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
            total_budget = await db.scalar(stmt)
            # 用户尚未设置月度总预算，此时不允许设置细分类目的预算
            if total_budget is None:
                return -4
        except Exception:
            return 0

        try:
            stmt = select(Bill_Category).where((Bill_Category.id == budget.category_id))
            category = await db.scalar(stmt)
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
            check = await db.scalar(stmt)
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
            check = await db.scalar(stmt)
            # 当月已存在同类预算
            if check is not None:
                return -7
        except Exception:
            return 0

    # 一切校验完成，才允许创建这个预算
    try:
        if budget.is_total == False:
            # 创建分类预算
            new_budget = Budget(
                user_id=budget.user_id,
                category_id=budget.category_id,
                is_total=budget.is_total,
                amount=budget.amount,
                month=budget.month
            )
        else:
            # 修复：创建总预算，显式设置category_id为None
            new_budget = Budget(
                user_id=budget.user_id,
                category_id=None,  # 总预算没有分类
                is_total=budget.is_total,
                amount=budget.amount,
                month=budget.month
            )
        db.add(new_budget)
        await db.flush()  # 刷新以获取数据库生成的ID
        await db.refresh(new_budget)  # 刷新对象以获取ID
        await db.commit()  # 提交事务
        return new_budget  # 返回新创建的预算对象（包含ID）
    except Exception:
        await db.rollback()  # 回滚事务
        # 尝试添加时发生数据库错误
        return 0


# 用于删除预算
async def budget_delete(budget: schemas.budget_delete, db: AsyncSession):
    stmt = select(User).where(User.id == budget.user_id)
    try:
        user = await db.scalar(stmt)
    except Exception:
        return 0
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Budget).where(Budget.id == budget.budget_id)
    try:
        target = await db.scalar(stmt)
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
            await db.execute(stmt)
        except Exception:
            return 0

    # 对目标记录进行删除
    try:
        await db.delete(target)
        return 1
    except Exception:
        return 0


# 用于修改预算（只能修改amount）
async def budget_update(budget: schemas.budget_update, db: AsyncSession):
    stmt = select(User).where(User.id == budget.user_id)
    try:
        user = await db.scalar(stmt)
    except Exception:
        return 0
    # 用户不存在
    if user is None:
        return -1

    stmt = select(Budget).where(Budget.id == budget.budget_id)
    try:
        target = await db.scalar(stmt)
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
        await db.execute(stmt)
        await db.commit()  # 提交事务
        # 修复：重新查询更新后的预算对象并返回
        stmt = select(Budget).where(Budget.id == budget.budget_id)
        updated_budget = await db.scalar(stmt)
        return updated_budget  # 返回更新后的预算对象
    except Exception:
        await db.rollback()  # 回滚事务
        return 0


# 用于获取某月的预算列表
async def budget_list_month(user_id: int, month: str, db: AsyncSession):
    stmt = select(User).where(User.id==user_id)
    try:
        user = await db.scalar(stmt)
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

    # 修复：不使用JOIN，直接查询Budget表
    stmt = select(
        Budget.id,
        Budget.category_id,
        Budget.is_total,
        Budget.amount,
        Budget.month,
        Budget.create_time,
        Budget.update_time
    ).where(
        (Budget.user_id == user_id) &
        (Budget.month == month)
    )
    try:
        result = await db.execute(stmt)
        result_list = result.all()
    except Exception:
        return 0

    result = []
    for record in result_list:
        item = {
            "id": record.id,
            "category_id": record.category_id,
            "is_total": record.is_total,
            "amount": record.amount,
            "month": record.month,
            "create_time": record.create_time,
            "update_time": record.update_time
        }
        
        # 修复：根据is_total判断name，而不是依赖JOIN
        if record.is_total:
            item["name"] = "本月总预算"
        else:
            # 获取分类名称
            try:
                stmt_cat = select(Bill_Category.name).where(
                    Bill_Category.id == record.category_id
                )
                category_name = await db.scalar(stmt_cat)
                item["name"] = category_name if category_name else "未知分类"
            except Exception:
                item["name"] = "未知分类"
        
        result.append(item)

    return result


"""
以下为可视化部分的查询函数
"""
# 获取近n天的消费趋势数据
async def get_trend_days(user_id: int, days: int, db: AsyncSession):
    stmt = select(User).filter(User.id==user_id)
    try:
        user = await db.scalar(stmt)
    except Exception:
        return 0
    if user is None:
        return -1

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)   # 回溯到n-1天前
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # 1. 生成完整的日期列表
    date_range = []
    current = start_date.date()
    end = end_date.date()
    while current <= end:
        date_range.append(current)
        current += timedelta(days=1)

    # 2. 优化：一次查询获取所有数据
    stmt = select(
        func.date(Bill.bill_time).label("date"),
        Bill_Category.type.label("category_type"),  # 1=收入, 2=支出
        func.sum(Bill.amount).label("amount")
    ).outerjoin(
        Bill_Category, Bill.category_id == Bill_Category.id
    ).filter(
        Bill.user_id == user_id,
        Bill_Category.type.in_([1, 2]),  # 同时查询收入和支出
        Bill.bill_time >= start_date,
        Bill.bill_time <= end_date
    ).group_by(
        func.date(Bill.bill_time),
        Bill_Category.type
    )

    try:
        result = await db.execute(stmt)
        results = result.all()
    except Exception:
        return 0

    # 3. 使用字典存储结果
    income_dict = defaultdict(float)
    expense_dict = defaultdict(float)

    for row in results:
        date_key = row.date
        if row.category_type == 1:  # 收入
            income_dict[date_key] = float(row.amount or 0)
        elif row.category_type == 2:  # 支出
            expense_dict[date_key] = float(row.amount or 0)

    # 4. 填充完整的日期列表
    income_list = []
    expense_list = []

    for date in date_range:
        # 收入列表
        income_amount = income_dict.get(date, 0.0)
        income_list.append({
            "date": date,
            "amount": income_amount
        })

        # 支出列表
        expense_amount = expense_dict.get(date, 0.0)
        expense_list.append({
            "date": date,
            "amount": expense_amount
        })

    return income_list, expense_list


# 获取近n个月的消费数据
async def get_trend_months(user_id: int, months: int, db: AsyncSession):
    stmt = select(User).filter(User.id == user_id)
    try:
        user = await db.scalar(stmt)
    except Exception:
        return 0
    if user is None:
        return -1

    # 2. 计算日期范围
    end_date = datetime.now()

    # 计算N个月前的第一天（确保整月）
    # 例如：今天是2024-03-15，近3个月就是：2024-01, 2024-02, 2024-03
    if end_date.day > 1:
        # 从本月1号开始算
        start_date = end_date.replace(day=1)
        # 再往前推(months-1)个月
        for _ in range(months - 1):
            # 计算上个月1号
            if start_date.month == 1:
                start_date = start_date.replace(year=start_date.year - 1, month=12)
            else:
                start_date = start_date.replace(month=start_date.month - 1)
    else:
        # 如果今天是1号，从本月开始算
        start_date = end_date.replace(day=1)
        # 再往前推(months-1)个月
        for _ in range(months - 1):
            if start_date.month == 1:
                start_date = start_date.replace(year=start_date.year - 1, month=12)
            else:
                start_date = start_date.replace(month=start_date.month - 1)

    # 给日期填充时间部分，以免第一天的数据无法获取
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # 生成月份列表
    month_range = []
    current = start_date
    while current <= end_date:
        month_str = current.strftime("%Y-%m")
        month_range.append(month_str)

        # 计算下个月1号
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    # 方法1：先查询所有数据，在Python中聚合
    stmt = select(
        Bill.bill_time,
        Bill_Category.type.label("category_type"),
        Bill.amount
    ).outerjoin(
        Bill_Category, Bill.category_id == Bill_Category.id
    ).filter(
        Bill.user_id == user_id,
        Bill_Category.type.in_([1, 2]),
        Bill.bill_time >= start_date,
        Bill.bill_time <= end_date
    )

    try:
        result = await db.execute(stmt)
        results = result.all()
    except Exception:
        return 0

    # 在Python中按月聚合
    income_dict = defaultdict(float)
    expense_dict = defaultdict(float)

    for row in results:
        if row.bill_time:
            month_key = row.bill_time.strftime("%Y-%m")
            if row.category_type == 1:  # 收入
                income_dict[month_key] += float(row.amount or 0)
            elif row.category_type == 2:  # 支出
                expense_dict[month_key] += float(row.amount or 0)

    # 6. 填充完整的月份列表
    income_list = []
    expense_list = []

    for month in month_range:
        # 解析年月
        year_str, month_str = month.split('-')
        year = int(year_str)
        month_num = int(month_str)

        # 收入列表
        income_amount = income_dict.get(month, 0.0)
        income_list.append({
            "time": month,
            "amount": income_amount,
        })

        # 支出列表
        expense_amount = expense_dict.get(month, 0.0)
        expense_list.append({
            "time": month,
            "amount": expense_amount,
        })

    return income_list, expense_list


# 获取近期账单
async def get_recent_bills(user_id: int, db: AsyncSession):
    stmt = select(User).filter(User.id == user_id)
    try:
        user = await db.scalar(stmt)
    except Exception:
        return 0
    if user is None:
        return -1

    stmt = select(
        Bill.bill_time,
        Bill_Category.name.label("category_name"),
        Bill.amount,
        Bill_Category.type.label("type"),
        Bill.remark
    ).join(
        Bill_Category, Bill.category_id == Bill_Category.id
    ).filter(
        Bill.user_id == user_id,
    ).order_by(desc(Bill.bill_time)).limit(6)

    try:
        result = await db.execute(stmt)
        bills = result.all()
    except Exception:
        return 0

    result_list = []
    for bill in bills:
        result_list.append({
            "bill_time": bill.bill_time,
            "category_name": bill.category_name,
            "amount": bill.amount,
            "type": bill.type,
            "remark": bill.remark
        })

    return result_list


# 获取预算使用情况分析
async def get_budget_usage(user_id: int, month: str, db: AsyncSession):
    # 1. 验证用户存在
    stmt = select(User).filter(User.id == user_id)
    try:
        user = await db.scalar(stmt)
    except Exception:
        return 0
    if user is None:
        return -1

    # 2. 验证月份格式
    try:
        start_time = datetime.strptime(f"{month}-01", "%Y-%m-%d")
    except Exception:
        return -2

    # 3. 计算该月的起止时间
    if start_time.month == 12:
        end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
    else:
        end_time = start_time.replace(month=start_time.month + 1, day=1)

    # 4. 查询该月的所有预算
    try:
        stmt = select(
            Budget.id,
            Budget.category_id,
            Budget.is_total,
            Budget.amount,
            Budget.month
        ).where(
            (Budget.user_id == user_id) &
            (Budget.month == month)
        )
        result = await db.execute(stmt)
        budgets = result.all()
    except Exception:
        return 0

    if not budgets:
        # 用户没有设置预算
        return month, {
            "has_budget": False,
            "total_budget": 0,
            "total_used": 0,
            "budget_list": []
        }

    # 5. 查询该月的实际支出
    try:
        stmt = select(
            Bill.category_id,
            func.sum(Bill.amount).label("total_amount")
        ).join(
            Bill_Category, Bill.category_id == Bill_Category.id
        ).filter(
            (Bill.user_id == user_id) &
            (Bill_Category.type == 2) &  # 只统计支出
            (Bill.bill_time >= start_time) &
            (Bill.bill_time < end_time)
        ).group_by(Bill.category_id)

        result = await db.execute(stmt)
        expenses = result.all()
    except Exception:
        return 0

    # 6. 构建分类支出字典
    expense_dict = {}
    total_expense = 0.0
    for expense in expenses:
        expense_dict[expense.category_id] = float(expense.total_amount or 0)
        total_expense += float(expense.total_amount or 0)

    # 7. 整合预算和支出数据
    budget_list = []
    total_budget = 0.0
    total_budget_item = None

    for budget in budgets:
        if budget.is_total:
            # 总预算
            total_budget = float(budget.amount)
            total_budget_item = {
                "id": budget.id,
                "name": "本月总预算",
                "category_id": None,
                "is_total": True,
                "budget_amount": float(budget.amount),
                "used_amount": total_expense,
                "remaining_amount": float(budget.amount) - total_expense,
                "usage_rate": (total_expense / float(budget.amount) * 100) if float(budget.amount) > 0 else 0,
                "status": "over" if total_expense > float(budget.amount) else "normal"
            }
        else:
            # 分类预算
            used = expense_dict.get(budget.category_id, 0.0)
            budget_amount = float(budget.amount)
            usage_rate = (used / budget_amount * 100) if budget_amount > 0 else 0

            # 获取分类名称
            try:
                stmt_cat = select(Bill_Category.name).where(Bill_Category.id == budget.category_id)
                category_name = await db.scalar(stmt_cat)
                name = category_name if category_name else "未知分类"
            except Exception:
                name = "未知分类"

            budget_list.append({
                "id": budget.id,
                "name": name,
                "category_id": budget.category_id,
                "is_total": False,
                "budget_amount": budget_amount,
                "used_amount": used,
                "remaining_amount": budget_amount - used,
                "usage_rate": usage_rate,
                "status": "over" if used > budget_amount else "normal"
            })

    # 按使用率降序排列
    budget_list.sort(key=lambda x: x["usage_rate"], reverse=True)

    # 8. 构建返回数据
    result_data = {
        "has_budget": True,
        "total_budget": total_budget,
        "total_used": total_expense,
        "total_remaining": total_budget - total_expense,
        "total_usage_rate": (total_expense / total_budget * 100) if total_budget > 0 else 0,
        "total_status": "over" if total_expense > total_budget else "normal",
        "total_info": total_budget_item,
        "budget_list": budget_list
    }

    return month, result_data


# 消费列别占比（单个月，month=-1时为全部，month=0时为当月，month=1时为上个月，以此类推，最多往后推12个月）
async def get_propotion_month(user_id: int, month: int, db: AsyncSession):
    # 1. 验证用户存在
    try:
        user = await db.scalar(select(User).filter(User.id == user_id))
    except Exception:
        return 0
    if user is None:
        return -1

    # 2. 根据month参数计算时间范围
    now = datetime.now()

    if month == -1:  # 全部历史数据
        start_date = None  # 不限制开始时间
        end_date = None  # 不限制结束时间
        period_description = "全部历史"
    else:
    # 计算下个月1号，然后减1秒得到本月最后时刻
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
        end_date = next_month - timedelta(seconds=1)
    # 计算目标月份
        target_year = now.year
        target_month = now.month - month    # 假如month是0，那么返回的就是当月的数据

        # 处理跨年
        while target_month < 1:
            target_month += 12
            target_year -= 1

        # 目标月份的第一天
        start_date = datetime(target_year, target_month, 1, 0, 0, 0)
        if month == 0:
            period_description = f"{target_year}年{target_month}月内"
        else:
            period_description = f"{target_year}年{target_month}月到{now.year}年{now.month}"

    # 3. 构建查询
    stmt = select(
        Bill_Category.name.label("category_name"),
        Bill_Category.id.label("category_id"),
        func.sum(Bill.amount).label("total_amount"),
        func.count(Bill.id).label("bill_count")
    ).join(
        Bill_Category, Bill.category_id == Bill_Category.id
    ).filter(
        Bill.user_id == user_id,
        Bill_Category.type == 2  # 只统计支出，收入不算占比
    )

    # 添加时间过滤（如果不是全部历史）
    if month != -1 and start_date and end_date:
        stmt = stmt.filter(
            Bill.bill_time >= start_date,
            Bill.bill_time <= end_date
        )

    # 按分类分组
    stmt = stmt.group_by(
        Bill_Category.name,
        Bill_Category.id
    ).order_by(
        func.sum(Bill.amount).desc()  # 按金额降序排列
    )


    try:
        result = await db.execute(stmt)
        results = result.all()
    except Exception:
        return 0

    # 4. 处理查询结果
    category_data = []
    total_amount = 0.0
    total_bills = 0

    for row in results:
        amount = float(row.total_amount or 0)
        count = row.bill_count or 0

        category_data.append({
            "category_id": row.category_id,
            "category_name": row.category_name,
            "amount": amount,
            "count": count
        })

        total_amount += amount
        total_bills += count

    # 5. 计算占比
    for item in category_data:
        if total_amount > 0:
            item["percentage"] = round((item["amount"] / total_amount) * 100, 2)
            item["proportion"] = f"{item['percentage']}%"
        else:
            item["percentage"] = 0.0
            item["proportion"] = "0%"

    # 6. 处理没有消费数据的情况
    if total_amount == 0:
        # 尝试获取所有分类（即使没有消费）
        result = await db.execute(
            select(Bill_Category.id, Bill_Category.name)
            .order_by(Bill_Category.id)
        )
        all_categories = result.all()

        for cat in all_categories:
            category_data.append({
                "category_id": cat.id,
                "category_name": cat.name,
                "amount": 0.0,
                "count": 0,
                "percentage": 0.0,
                "proportion": "0%"
            })

    # 7. 返回结构化的结果
    return period_description, category_data


# 获取支付方式分布
async def get_payment_method_distribution(user_id: int, month: str, db: AsyncSession):
    # 1. 验证用户存在
    stmt = select(User).filter(User.id == user_id)
    try:
        user = await db.scalar(stmt)
    except Exception:
        return 0
    if user is None:
        return -1

    # 2. 构建时间范围
    if month == "all" or month == "-1":
        # 查询全部历史数据
        start_date = None
        end_date = None
        period_description = "全部历史"
    else:
        # 验证月份格式
        try:
            start_time = datetime.strptime(f"{month}-01", "%Y-%m-%d")
        except Exception:
            return -2

        # 计算该月的起止时间
        if start_time.month == 12:
            end_time = start_time.replace(year=start_time.year + 1, month=1, day=1)
        else:
            end_time = start_time.replace(month=start_time.month + 1, day=1)

        start_date = start_time
        end_date = end_time
        period_description = month

    # 3. 查询支付方式的消费统计（只统计支出）
    try:
        stmt = select(
            Payment_Method.id.label("method_id"),
            Payment_Method.name.label("method_name"),
            func.sum(Bill.amount).label("total_amount"),
            func.count(Bill.id).label("bill_count")
        ).join(
            Bill, Payment_Method.id == Bill.method_id
        ).join(
            Bill_Category, Bill.category_id == Bill_Category.id
        ).filter(
            Bill.user_id == user_id,
            Bill_Category.type == 2  # 只统计支出
        )

        # 添加时间过滤（如果不是全部历史）
        if start_date and end_date:
            stmt = stmt.filter(
                Bill.bill_time >= start_date,
                Bill.bill_time < end_date
            )

        # 按支付方式分组
        stmt = stmt.group_by(
            Payment_Method.id,
            Payment_Method.name
        ).order_by(
            func.sum(Bill.amount).desc()  # 按金额降序排列
        )

        result = await db.execute(stmt)
        results = result.all()
    except Exception:
        return 0

    # 4. 处理查询结果
    method_data = []
    total_amount = 0.0
    total_bills = 0

    for row in results:
        amount = float(row.total_amount or 0)
        count = row.bill_count or 0

        method_data.append({
            "method_id": row.method_id,
            "method_name": row.method_name,
            "amount": amount,
            "count": count
        })

        total_amount += amount
        total_bills += count

    # 5. 计算占比
    for item in method_data:
        if total_amount > 0:
            item["percentage"] = round((item["amount"] / total_amount) * 100, 2)
            item["proportion"] = f"{item['percentage']}%"
        else:
            item["percentage"] = 0.0
            item["proportion"] = "0%"

    # 6. 处理没有消费数据的情况
    if total_amount == 0:
        # 尝试获取所有支付方式（即使没有消费）
        result = await db.execute(
            select(Payment_Method.id, Payment_Method.name)
            .order_by(Payment_Method.id)
        )
        all_methods = result.all()

        for method in all_methods:
            method_data.append({
                "method_id": method.id,
                "method_name": method.name,
                "amount": 0.0,
                "count": 0,
                "percentage": 0.0,
                "proportion": "0%"
            })

    # 7. 返回结构化的结果
    result_data = {
        "total_amount": total_amount,
        "total_bills": total_bills,
        "method_list": method_data
    }

    return period_description, result_data

