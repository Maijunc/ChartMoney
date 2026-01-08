from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# ⚠️ 注意修改这里的密码！
# 格式: mysql+pymysql://用户名:密码@IP:端口/数据库名
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/finance_db"

# 修改前
# ...@localhost:3306/...

# 修改后 (强制指定 IPv4)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/finance_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db   # 返回数据库会话给函数
        db.commit()    # 无异常，提交事务
    except Exception:
        db.rollback()  # 有异常，回滚
        raise   # 将异常向上提交，以便上层进行可能的异常处理
    finally:
        db.close()     # 关闭这个会话