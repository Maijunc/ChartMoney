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


# 用户登录处理函数
@app.post("/user/login")
def user_login(user: schemas.User, db: Session = Depends(database.get_db)):
    # ↑Depends依赖注入的一定是可调用函数对象，且Depends必须在处理函数中使用才会有效
    result = crud.user_login(user, db)
    if result:
        return {
            "code": 200,
            "message": "success"
        }
    else:
        return {
            "code": "401",
            "message": "failure"
        }


# 用户注册处理函数
@app.post("/user/register")
def user_resgister(user: schemas.User_register, db: Session = Depends(database.get_db)):
    result = crud.user_register(user, db)
    if result == 1:
        return {
            "code": 200,
            "message": "success"
        }
    elif result == -1:
        return {
            "code": 400,
	        "message": "username already exists"
        }
    elif result == -2:
        return {
            "code": 400,
            "message": "the phone number already exists"
        }
    elif result == 0:
        return {
            "code": 400,
            "message": "operational error"
        }


# 账单分类创建处理函数
@app.post("/bill_category/add")
def bill_category_add(bill_category: schemas.bill_category_add, db: Session = Depends(database.get_db)):
    result = crud.bill_category_add(bill_category, db)
    if result == 1:
        return {
            "code": 200,
            "message": "success"
        }
    elif result == 0:
        return {
            "code": 5001,
            "message": "unable to be inserted into the database"
        }
    elif result == -1 or result == -2:
        return {
            "code": 400,
            "message": "category already exist"
        }


# 账单分类修改处理函数
@app.put("/bill_category/update")
def bill_category_update(bill_category: schemas.bill_category_update, db: Session = Depends(database.get_db)):
    result = crud.bill_category_update(bill_category, db)
    if result == 1:
        return {
            "code": 200,
            "message": "success"
        }
    elif result == 0:
        return {
            "code": 5001,
            "message": "unable to be inserted into the database"
        }
    elif result == -1:
        return {
            "code": 404,
            "message": "target category does not exist"
        }
    elif result == -2:
        return{
            "code": 401,
            "message": "can not revise a system preset category"
        }
    elif result == -3:
        return {
            "code": 401,
            "message": "can not revise other user's category"
        }
    elif result == -4 or result == -5:
        return {
            "code": 400,
            "message": "category already exist"
        }