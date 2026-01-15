from sqlalchemy import func, String, BigInteger, DateTime, ForeignKey, Boolean, DECIMAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import TINYINT   # TINYINT是MySql数据库特有类型，属于方言
from typing import List
from datetime import datetime


class Base(DeclarativeBase):    # 这是一个模型类的基类，可用于创建所有子类的元数据，所有模型类共有的属性可以写在这里
    create_time: Mapped[datetime] = mapped_column(  # 创建时间为所有表共有属性
        type_=DateTime,
        default=func.now(),
        server_default=func.now(),
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(  # 更新时间为所有表的共有属性
        type_=DateTime,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )


class User(Base):   # 用户表的模型类
    __tablename__ = "user"

    # id从1开始自递增
    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="用户id", autoincrement=True)
    username: Mapped[str] = mapped_column(type_=String(20), comment="用户名", nullable=False, unique=True)
    password: Mapped[str] = mapped_column(type_=String(64), comment="用户密码", nullable=False)
    phone: Mapped[str] = mapped_column(type_=String(11), comment="电话号码", nullable=False, unique=True)
    avatar: Mapped[str] = mapped_column(type_=String(255), comment="头像地址", nullable=True)

    bill_categories: Mapped[List["Bill_Category"]] = relationship(back_populates="user")    # 一个用户对应多个分类，使用List
    bills: Mapped[List["Bill"]] = relationship(back_populates="user")   # 一个用户对应多个账单
    budgets: Mapped[List["Budget"]] = relationship(back_populates="user")   # 一个用户对应多个预算


class Bill_Category(Base):
    __tablename__ = "bill_category"

    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="分类id", autoincrement=True)
    name: Mapped[str] = mapped_column(type_=String(20), comment="分类名称", nullable=False)
    type: Mapped[int] = mapped_column(type_=TINYINT, comment="1为收入分类，2为支出分类", nullable=False)

    user: Mapped["User"] = relationship(back_populates="bill_categories", uselist=False)  # 一个账单分类对应一个用户
    bills: Mapped[List["Bill"]] = relationship(back_populates="bill_category")    # 一个账单分类对应多个账单
    budgets: Mapped[List["Budget"]] = relationship(back_populates="bill_category")  # 一个账单分类对应多个预算


class Bill(Base):
    __tablename__ = "bill"

    id: Mapped[int] = mapped_column(type_=BigInteger ,primary_key=True, comment="账单id", autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("bill_category.id"))
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, comment="金额")
    remark: Mapped[str] = mapped_column(String(255), nullable=True, comment="账单备注")
    bill_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="订单发生时间")

    user: Mapped["User"] = relationship(back_populates="bills", uselist=False)   # 一个账单对应一个用户
    bill_category: Mapped["Bill_Category"] = relationship(back_populates="bills", uselist=False)    # 一个账单对应一个分类


class Budget(Base):
    __tablename__ = "budget"

    id: Mapped[int] = mapped_column(type_=BigInteger, primary_key=True, comment="预算id", autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"))
    # category_id为null时做额外判断
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("bill_category.id"), nullable=True)
    is_total: Mapped[bool] = mapped_column(type_=Boolean, default=False, comment="是否是月度总预算")
    amount: Mapped[float] = mapped_column(type_=DECIMAL(10, 2), nullable=False, comment="金额")
    month: Mapped[str] = mapped_column(type_=String(7), nullable=False, comment="月份")

    user: Mapped["User"] = relationship(back_populates="budgets", uselist=False) # 一个预算对应一个用户
    bill_category: Mapped["Bill_Category"] = relationship(back_populates="budgets", uselist=False)   # 一个预算对应一个分类