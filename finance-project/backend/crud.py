from models import User
from sqlalchemy.orm import Session
from sqlalchemy import select

"""
本模块主要负责进行对数据库的增删改查
"""

# 用于用户登录时，查看用户名和密码是否正确，正确就会返回True
def user_login(username: str, password: str, db: Session):
    result = db.execute(select(User).where((User.username == username)))
    user = result.scalar_one_or_none()
    if user is not None:
        if user.password == password:
            return True
        else:
            return False
    else:
        return False