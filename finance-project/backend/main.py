from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database, models, schemas, crud

# 启动时自动在数据库建表 (C++思维：类似编译时链接)
models.Base.metadata.create_all(bind=database.engine)   # 创建所有以Base类为基类的模型类的元数据

app = FastAPI()

# 允许前端跨域访问 (必配！)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，实训可以用 *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}


@app.post("/user/login")
def user_login(user: schemas.User, db: Session = Depends(database.get_db)):     # Depends依赖注入的一定是可调用函数对象
    result = crud.user_login(user.username, user.password, db)
    if result:
        return {
            "code": "200",
            "result": "success"
        }
    else:
        return {
            "code": "401",
            "result": "failure"
        }