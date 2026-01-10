from models import User, Bill_Category
from sqlalchemy.orm import Session
from sqlalchemy import select
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
def bill_category_add(bill_category: schemas.bill_category_add, db: Session):
    # 检查用户此前是否添加过同名的分类
    check1 = db.execute(select(Bill_Category).where((Bill_Category.user_id == bill_category.user_id)
                & (Bill_Category.name == bill_category.name)))
    check_result1 = check1.scalar_one_or_none()

    # 检查用户是否试图添加一个同系统分类同名的分类
    check2 = db.execute(select(Bill_Category).where((Bill_Category.is_sys == True)
                & (Bill_Category.name == bill_category.name)))
    check_result2 = check2.scalar_one_or_none()

    if check_result1 is not None:
        return -1
    if check_result2 is not None:
        return -2

    new_bill_category = Bill_Category(user_id=bill_category.user_id, is_sys=False, name=bill_category.name)
    try:
        db.add(new_bill_category)
        db.commit()
        return 1
    except Exception:
        return 0    # 数据库插入失败