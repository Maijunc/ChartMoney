from models import User
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
        db.add(user)
        db.commit()
        return 1
    except Exception:
        return 0