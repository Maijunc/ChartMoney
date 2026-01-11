from models import User, Bill_Category
from sqlalchemy.orm import Session
from sqlalchemy import select, update
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


# 用于创建账单分类
def category_add(category: schemas.category_add, db: Session):
    # 检查用户此前是否添加过同名的分类
    check1 = db.execute(select(Bill_Category).where((Bill_Category.user_id == category.user_id)
                & (Bill_Category.name == category.name)))
    check_result1 = check1.scalar_one_or_none()

    # 检查用户是否试图添加一个同系统分类同名的分类
    check2 = db.execute(select(Bill_Category).where((Bill_Category.is_sys == True)
                & (Bill_Category.name == category.name)))
    check_result2 = check2.scalar_one_or_none()

    if check_result1 is not None:
        return -1
    if check_result2 is not None:
        return -2

    new_category = Bill_Category(user_id=category.user_id, is_sys=False, name=category.name)
    try:
        db.add(new_category)
        db.commit()
        return 1
    except Exception:
        return 0    # 数据库插入失败


# 用于修改账单分类
def category_update(category: schemas.category_update, db: Session):
    # update_category = db.query(Bill_Category).filter(Bill_Category.id == category.category_id).first()
    update_category = db.execute(select(Bill_Category).where(Bill_Category.id == category.category_id))\
        .scalar_one_or_none()

    # 分类不存在
    if update_category is None:
        return -1
    else:
        # 用户不能修改系统预设分类
        if update_category.is_sys == True:
            return -2

        # 用户无权修改别的用户的分类
        if update_category.user_id != category.user_id:
            return  -3

        # 检查修改后的分类名是否和用户已有的分类名重复
        check1 = db.execute(select(Bill_Category).where((Bill_Category.user_id == category.user_id)
                                                        & (Bill_Category.name == category.name)))
        check_result1 = check1.scalar_one_or_none()

        # 检查修改后的分类名是否和系统分类名重复
        check2 = db.execute(select(Bill_Category).where((Bill_Category.is_sys == True)
                                                        & (Bill_Category.name == category.name)))
        check_result2 = check2.scalar_one_or_none()

        if check_result1 is not None:
            return -4
        if check_result2 is not None:
            return -5

        else:
            try:
                stmt = update(Bill_Category).where(Bill_Category.id==category.category_id).values(
                    name=category.name
                )
                db.execute(stmt)
                db.commit()
                return 1
            except Exception:
                # 数据库修改失败
                return 0


# 用于删除账单分类
def category_delete(category: schemas.category_delete, db: Session):
    delete_category = db.query(Bill_Category).where(Bill_Category.id==category.category_id).first()

    # 不存在此分类
    if delete_category is None:
        return -1
    # 不能删除系统预设分类
    elif delete_category.is_sys is True:
        return -2
    # 不能删除别的用户的分类
    elif delete_category.user_id != category.user_id:
        return -3
    else:
        # 尝试进行删除操作
        try:
            db.delete(delete_category)
            db.commit()
            return 1
        except Exception:
            # 数据库修改失败
            return 0


# 用于获取用户的账单分类列表
def category_list(user_id: int, db: Session):
    # 先查看传入的用户id是否存在
    stmt = select(User).where(User.id == user_id)
    check = db.scalar(stmt)
    if check is None:
        return 0

    # 获取系统预设分类(需要使用scalars)
    stmt = select(Bill_Category).where(Bill_Category.is_sys == True)
    sys_category = db.scalars(stmt).all()

    # 获取用户自定义的分类
    stmt = select(Bill_Category).where(Bill_Category.user_id == user_id)
    user_category = db.scalars(stmt).all()

    result_list = []

    for category in sys_category:
        result_list.append({
            "category_id": category.id,
            "user_id": category.user_id,
            "is_sys": category.is_sys,
            "name": category.name,
            "create_time": category.create_time,
            "update_time": category.update_time
        })
    for category in user_category:
        result_list.append({
            "category_id": category.id,
            "user_id": category.user_id,
            "is_sys": category.is_sys,
            "name": category.name,
            "create_time": category.create_time,
            "update_time": category.update_time
        })

    return result_list