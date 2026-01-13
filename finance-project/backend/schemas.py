from pydantic import BaseModel, Field
from datetime import datetime


"""
此文件用于存放请求体类
"""


# 用于用户登录
class User(BaseModel):
    # 除了指定输入什么数据外，还要能对数据的格式做限制
    username: str = Field(..., min_length=1, max_length=20)     # Field用于增加对于参数的约束
    password: str = Field(..., min_length=1, max_length=64)


# 用于用户注册
class User_register(BaseModel):
    # 必须接收用户名和手机号作为参数，且用户名和手机号在数据库中都必须唯一
    username: str = Field(..., min_length=1, max_length=20)
    # 手机号必须为11位，且是以1开头的11位数字
    phone: str = Field(..., min_length=11, max_length=11, pattern=r"^1\d{10}$")
    password: str = Field(..., min_length=1, max_length=64)


# 用于创建账单分类
class category_add(BaseModel):
    user_id: int = Field(..., ge=1)     # 必填且大于1
    name: str = Field(..., min_length=1, max_length=20)
    type: int = Field(..., ge=1, le=2)


# 用于修改账单分类名
class category_update(BaseModel):
    user_id: int = Field(..., ge=1)
    category_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=20)
    type: int = Field(..., ge=1, le=2)


# 用于删除账单分类
class category_delete(BaseModel):
    user_id: int = Field(..., ge=1)
    category_id: int = Field(..., ge=1)


# 用于添加账单
class bill_add(BaseModel):
    user_id: int = Field(..., ge=1)
    category_id: int = Field(..., ge=1)
    amount: float = Field(..., gt=0)
    bill_time: datetime
    remark: str = Field(max_length=255)


# 用于修改账单
class bill_update(BaseModel):
    user_id: int = Field(..., ge=1)
    category_id: int = Field(..., ge=1)
    bill_id: int = Field(..., ge=1)
    amount: float = Field(..., gt=0)
    bill_time: datetime
    remark: str = Field(max_length=255)


# 用于删除账单
class bill_delete(BaseModel):
    user_id: int = Field(..., ge=1)
    bill_id: int = Field(..., ge=1)


class budget_add(BaseModel):
    user_id: int = Field(..., ge=1)
    category_id: int
    is_total: bool
    amount: float = Field(..., gt=0)
    month: str = Field(..., min_length=7, max_length=7)
    month: str = Field(..., min_length=7, max_length=7)