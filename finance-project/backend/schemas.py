from pydantic import BaseModel, Field


class User(BaseModel):
    # 除了指定输入什么数据外，还要能对数据的格式做限制
    username: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=1, max_length=64)