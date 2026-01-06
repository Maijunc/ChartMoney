from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ⚠️ 注意修改这里的密码！
# 格式: mysql+pymysql://用户名:密码@IP:端口/数据库名
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/finance_db"

# 修改前
# ...@localhost:3306/...

# 修改后 (强制指定 IPv4)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/finance_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()