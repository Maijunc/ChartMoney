from sqlalchemy import func, Column, String, BigInteger, DateTime, ForeignKey, Boolean, DECIMAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import TINYINT   # TINYINT是MySql数据库特有类型，属于方言
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
    bills: Mapped[List["Bill"]] = relationship(back_populates="user")   # 一个用户对应多个账单


class Bill_Category(Base):
    __tablename__ = "bill_category"

    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="分类id", autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True)    # 外键（应可空）
    is_sys: Mapped[bool] = mapped_column(type_=Boolean, default=False, comment="是否是系统分类")
    name: Mapped[str] = mapped_column(type_=String(20), comment="分类名称", nullable=False)

    user: Mapped["User"] = relationship(back_populates="bill_category", uselist=False)  # 一个账单分类对应一个用户
    bills: Mapped["Bill"] = relationship(back_populates="bill_category")    # 一个账单分类对应多个账单


class Bill(Base):
    __tablename__ = "bill"

    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="账单id", autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("bill_category.id"))
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, comment="金额")
    type: Mapped[int] = mapped_column(TINYINT, nullable=False, comment="1代表收入，2代表支出")
    remark: Mapped[str] = mapped_column(String(255), nullable=True, comment="账单备注")
    bill_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="订单发生时间")
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

    user: Mapped["User"] = relationship(back_populates="bill", uselist=False)   # 一个账单对应一个用户
    bill_category: Mapped["Bill_Category"] = relationship(back_populates="bill", uselist=False)    # 一个账单对应一个分类


