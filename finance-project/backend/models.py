from sqlalchemy import func, Column, String, BigInteger, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
from datetime import datetime


class Base(DeclarativeBase):    # 这是一个模型类的基类，可用于创建所有子类的元数据，所有模型类共有的属性可以写在这里
    pass


class User(Base):   # 用户表的模型类
    __tablename__ = "user"

    # id从1开始自递增
    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="用户id", autoincrement=True)
    username: Mapped[str] = mapped_column(type_=String(20), comment="用户名", nullable=False)
    password: Mapped[str] = mapped_column(type_=String(64), comment="用户密码", nullable=False)
    phone: Mapped[str] = mapped_column(type_=String(11), comment="电话号码", nullable=False)
    avatar: Mapped[str] = mapped_column(type_=String(255), comment="头像地址")
    create_time: Mapped[datetime] = mapped_column(
        type_=DateTime,
        default=func.now(),
        server_default=func.now(),
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        type_=DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    bill_categories: Mapped[List["Bill_Category"]] = relationship(back_populates="user")    # 一个用户对应多个分类，使用List


class Bill_Category(Base):
    __tablename__ = "bill_category"

    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="分类id", autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True)    # 外键（应可空）
    is_sys: Mapped[bool] = mapped_column(type_=Boolean, default=False, comment="是否是系统分类")
    name: Mapped[str] = mapped_column(type_=String(20), comment="分类名称", nullable=False)

    user: Mapped["User"] = relationship(back_populates="bill_category", uselist=False)  # 一个账单分类对应一个用户
