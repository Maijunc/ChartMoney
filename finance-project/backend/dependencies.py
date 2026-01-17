"""
依赖函数模块
提供 FastAPI 依赖注入使用的函数，如 Token 验证
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import security
import database
from models import User

# HTTP Bearer Token 认证方案
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(database.get_db)
) -> User:
    """
    从请求头中获取 Token 并验证，返回当前登录用户

    使用方法：
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}

    Args:
        credentials: HTTP Bearer Token
        db: 数据库会话

    Returns:
        当前登录的用户对象

    Raises:
        HTTPException: Token 无效或用户不存在
    """
    token = credentials.credentials

    # 验证 Token
    payload = security.verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从 Token 中获取 user_id
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 从数据库查询用户
    from sqlalchemy import select
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_id(current_user: User = Depends(get_current_user)) -> int:
    """
    获取当前登录用户的 ID（简化版）

    使用方法：
        @app.get("/my-data")
        def my_data(user_id: int = Depends(get_current_user_id)):
            return {"user_id": user_id}

    Args:
        current_user: 当前用户对象

    Returns:
        用户 ID
    """
    return current_user.id
