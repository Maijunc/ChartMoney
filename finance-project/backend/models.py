from sqlalchemy import func, Column, String, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):    # 这是一个模型类的基类，可用于创建所有子类的元数据，所有模型类共有的属性可以写在这里
    pass
class user(Base):   # 用户表的模型类
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="用户id")
    username: Mapped[str] = mapped_column(type_=String(20), comment="用户名", nullable=False)
    password: Mapped[str] = mapped_column(type_=String(64), comment="用户密码", nullable=False)
    phone: Mapped[str] = mapped_column(type_=String(11), comment="电话号码", nullable=False)
    avatar: Mapped[str] = mapped_column(type_=String(255), comment="头像地址")
    create_time: Mapped[datetime] = mapped_column(type_=DateTime, default=func.now(), server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime] = mapped_column(type_=DateTime, default=func.now(), server_default=func.now(), onupdate=func.now(), comment="更新时间")
