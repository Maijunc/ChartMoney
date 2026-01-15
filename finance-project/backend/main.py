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


# # 账单分类创建处理函数
# @app.post("/category/add")
# def bill_category_add(category: schemas.category_add, db: Session = Depends(database.get_db)):
#     result = crud.category_add(category, db)
#     if result == 1:
#         return {
#             "code": 200,
#             "message": "success"
#         }
#     elif result == 0:
#         return {
#             "code": 5001,
#             "message": "unable to be inserted into the database"
#         }
#     elif result == -1:
#         return {
#             "code": 401,
#             "message": "don't have such user"
#         }
#     elif result == -2:
#         return {
#             "code": 400,
#             "message": "a category with the same name already exists"
#         }


# # 账单分类修改处理函数
# @app.put("/category/update")
# def bill_category_update(category: schemas.category_update, db: Session = Depends(database.get_db)):
#     result = crud.category_update(category, db)
#     if result == 1:
#         return {
#             "code": 200,
#             "message": "success"
#         }
#     elif result == 0:
#         return {
#             "code": 5001,
#             "message": "failed to update database records"
#         }
#     elif result == -1:
#         return {
#             "code": 401,
#             "message": "the user does not exist"
#         }
#     elif result == -2 or result == -4:
#         return {
#             "code": 400,
#             "message": "don't have such category"
#         }
#     elif result == -3:
#         return {
#             "code": 401,
#             "message": "the preset classification of the system cannot be modified"
#         }
#     elif result == -5:
#         return {
#             "code": 401,
#             "message": "the same classification already exists, so this modification is ineffective"
#         }


# # 账单分类删除
# @app.delete("/category/delete")
# def bill_category_delete(category: schemas.category_delete, db: Session = Depends(database.get_db)):
#     result = crud.category_delete(category, db)
#
#     if result == 1:
#         return {
#             "code": 200,
#             "message": "success"
#         }
#     elif result == 0:
#         return {
#             "code": 5001,
#             "message": "cannot delete from the database"
#         }
#     elif result == -1:
#         return {
#             "code": 404,
#             "message": "category does not exist"
#         }
#     elif result == -2:
#         return {
#             "code": 401,
#             "message": "cannot delete system preset category"
#         }
#     elif result == -3:
#         return {
#             "code": 401,
#             "message": "cannot delete other user's category"
#         }
#     elif result == -4:
#         return {
#             "code": 400,
#             "message": "this category has bills associated with it and cannot be deleted"
#         }


# 获取账单分类列表
@app.get("/category/list")
def bill_category_list(type: int, db: Session = Depends(database.get_db)):
    if type not in [1, 2]:
        return {
            "code": "400",
            "message": "incorrect input of types",
            "data": []
        }

    result = crud.category_list(type, db)
    if result == 0:
        return {
            "code": "5001",
            "message": "error occurred while querying the database",
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
            "message": "an error occurred while accessing the database"
        }
    elif result == -1:
        return {
            "code": 401,
            "message": "user does not exist"
        }
    elif result == -2:
        return {
            "code": 401,
            "message": "category does not exist"
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
            "message": "an error occurred while accessing the database"
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
            "message": "an error occurred while accessing the database"
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


# 获取账单列表
@app.get("/bill/list")
def bill_list(user_id: int, the_time: str, page:int, page_size: int, type: int, db: Session = Depends(database.get_db)):
    if page_size <15:
        return {
            "code": 400,
            "message": "abnormal page size",
            "data": []
        }
    if type not in [1, 2]:
        return {
            "code": 400,
            "message": "abnormal page size",
            "data": []
        }
    # 验证月份是否有效（1-12月）
    try:
        year_str, month_str = the_time.split('-')
        year = int(year_str)
        month = int(month_str)

        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        return {
            "code": 400,
            "message": "incorrect time format",
            "data": []
        }
    temp = crud.get_bill_count(user_id, the_time, page_size, type, db)
    if temp == 0:
        return {
            "code": 5001,
            "message": "database error",
            "data": []
        }
    elif temp == -1:
        return {
            "code": 401,
            "message": "don't have such user",
            "data": []
        }
    total = temp["total"]
    page_num = temp["page_num"]
    if total == 0:
        return {
            "code": 200,
            "message": "success",
            "total": total,
            "page_num": page_num,
            "data": []
        }

    if page < 1 or page > page_num:
        return {
            "code": 400,
            "message": "page does not exit",
            "data": []
        }

    result = crud.bill_list(user_id, the_time, page, page_size, type, db)
    if result == 0:
        return {
            "code": 5001,
            "message": "database error",
            "data": []
        }
    else:
        return {
            "code": 200,
            "message": "success",
            "total": total,
            "page_num": page_num,
            "data": result
        }


# 用于添加预算
@app.post("/budget/add")
def budget_add(budget: schemas.budget_add, db: Session = Depends(database.get_db)):
    result = crud.budget_add(budget, db)

    if result == 1:
        return {
            "code": 200,
            "message": "success"
        }
    elif result == 0:
        return {
            "code": 5001,
            "message": "an error occurred while accessing the database"
        }
    elif result == -1:
        return {
            "code": 400,
            "message": "the data input is incorrect"
        }
    elif result == -2:
        return {
            "code": 400,
            "message": "incorrect date format"
        }
    elif result == -3:
        return {
            "code": 401,
            "message": "the user does not exist"
        }
    elif result == -4:
        return {
            "code": 400,
            "message": "The monthly overall budget has not been set yet. It is necessary to set the monthly overall "
                       "budget first"
        }
    elif result == -5:
        return {
            "code": 400,
            "message": "don't have such category"
        }
    elif result == -6:
        return {
            "code": 5001,
            "message": "the same type of budget for that month already exists"
        }
    elif result == -7:
        return {
            "code": 5001,
            "message": "The total of all the monthly budgets has exceeded the monthly overall budget. This budget "
                       "cannot be created. It is necessary to first modify the monthly overall budget."
        }