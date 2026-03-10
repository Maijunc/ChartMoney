from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import models

# ⚠️ 注意修改这里的密码！
# 格式: mysql+aiomysql://用户名:密码@IP:端口/数据库名
# ASYNC_SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/finance_db"

# 修改前
# ...@localhost:3306/...

# 修改后 (强制指定 IPv4，使用 aiomysql 异步驱动)
ASYNC_SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:wufulin951753.@127.0.0.1:3306/finance_db"

# 创建异步引擎
engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    echo=False,  # 生产环境设为 False
    pool_pre_ping=True,  # 连接健康检查
    pool_recycle=3600,  # 连接回收时间
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False
)

async def get_db():
    """
    异步数据库依赖注入函数
    返回异步数据库会话
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db   # 返回数据库会话给函数
            await db.commit()    # 无异常，提交事务
        except Exception:
            await db.rollback()  # 有异常，回滚
            raise   # 将异常向上提交，以便上层进行可能的异常处理
        finally:
            await db.close()     # 关闭这个会话