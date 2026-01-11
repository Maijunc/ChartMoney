from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database, models, schemas, crud

# 启动时自动在数据库建表 (C++思维：类似编译时链接)
models.Base.metadata.create_all(bind=database.engine)  # 创建所有以Base类为基类的模型类的元数据

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
@app.post("/category/add")
def bill_category_add(category: schemas.category_add, db: Session = Depends(database.get_db)):
    result = crud.category_add(category, db)
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
@app.put("/category/update")
def bill_category_update(category: schemas.category_update, db: Session = Depends(database.get_db)):
    result = crud.category_update(category, db)
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
        return {
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


# 账单分类删除
@app.delete("/category/delete")
def bill_category_delete(category: schemas.category_delete, db: Session = Depends(database.get_db)):
    result = crud.category_delete(category, db)

    if result == 1:
        return {
            "code": 200,
            "message": "success"
        }
    elif result == 0:
        return {
            "code": 5001,
            "message": "cannot delete from the database"
        }
    elif result == -1:
        return {
            "code": 404,
            "message": "category does not exist"
        }
    elif result == -2:
        return {
            "code": 401,
            "message": "cannot delete system preset category"
        }
    elif result == -3:
        return {
            "code": 401,
            "message": "cannot delete other user's category"
        }
    elif result == -4:
        return {
            "code": 400,
            "message": "this category has bills associated with it and cannot be deleted"
        }


# 获取账单分类列表
@app.get("/category/list")
def bill_category_list(user_id: int, db: Session = Depends(database.get_db)):
    result = crud.category_list(user_id, db)
    if result == 0:
        return {
            "code": "401",
            "message": "user does not exist",
            "data": []
        }
    else:
        return {
            "code": "200",
            "message": "success",
            "data": result
        }


# 创建订单
@app.post("/bill/add")
def bill_add(bill: schemas.bill_add, db: Session = Depends(database.get_db)):
    result = crud.bill_add(bill, db)

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
            "code": 401,
            "message": "user does not exist"
        }
    elif result == -2:
        return {
            "code": 401,
            "message": "category does not exist, the user does not have such category"
        }


# 修改订单
@app.put("/bill/update")
def bill_update(bill: schemas.bill_update, db: Session = Depends(database.get_db)):
    result = crud.bill_update(bill, db)

    if result == 1:
        return {
            "code": 200,
            "message": "success"
        }
    elif result == 0:
        return {
            "code": 5001,
            "message": "failed to modify the database"
        }
    elif result == -1:
        return {
            "code": 401,
            "message": "user does not exist"
        }
    elif result == -2:
        return {
            "code": 400,
            "message": "category does not exist"
        }
    elif result == -3:
        return {
            "code": 400,
            "message": "the bill does not exist"
        }
    elif result == -4:
        return {
            "code": 401,
            "message": "this user does not have such a category"
        }
    elif result == -5:
        return {
            "code": 401,
            "message": "this user does not have such a bill"
        }


# 删除账单
@app.delete("/bill/delete")
def bill_delete(bill: schemas.bill_delete, db: Session = Depends(database.get_db)):
    result = crud.bill_delete(bill, db)

    if result == 1:
        return {
            "code": 200,
            "message": "success"
        }
    elif result == 0:
        return {
            "code": 5001,
            "message": "the deletion operation in the database failed"
        }
    elif result == -1:
        return {
            "code": 401,
            "message": "user does not exist"
        }
    elif result == -2:
        return {
            "code": 400,
            "message": "the bill does not exist"
        }
    elif result == -3:
        return {
            "code": 401,
            "meaage": "the user does not have such a bill"
        }