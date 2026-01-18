import fastapi
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from sqlalchemy.orm import Session
import database, models, schemas, crud, security
from dependencies import get_current_user, get_current_user_id

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


# 测试 Token 认证的受保护接口
@app.get("/user/me")
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """
    获取当前登录用户的信息（需要 Token）

    请求头需要包含：
    Authorization: Bearer <token>
    """
    return {
        "code": status.HTTP_200_OK,
        "message": "获取成功",
        "data": {
            "user_id": current_user.id,
            "username": current_user.username,
            "phone": current_user.phone,
            "avatar": current_user.avatar if current_user.avatar else ""
        }
    }


# 用户登录处理函数
@app.post("/user/login")
def user_login(user: schemas.User, db: Session = Depends(database.get_db)):
    # ↑Depends依赖注入的一定是可调用函数对象，且Depends必须在处理函数中使用才会有效
    result = crud.user_login(user, db)

    # result 现在是用户对象或 None
    if result:
        # 生成 JWT Token
        access_token = security.create_access_token(
            data={"user_id": result.id, "username": result.username}
        )

        return {
            "code": status.HTTP_200_OK,
            "message": "登录成功",
            "data": {
                "user_id": result.id,
                "username": result.username,
                "phone": result.phone,
                "avatar": result.avatar if result.avatar else "",  # 头像可能为空
                "token": access_token  # 返回 JWT Token
            }
        }
    else:
        # 统一返回"用户名或密码错误"，不区分是用户不存在还是密码错误（安全考虑）
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")


# 用户注册处理函数
@app.post("/user/register")
def user_register(user: schemas.User_register, db: Session = Depends(database.get_db)):
    result = crud.user_register(user, db)

    # result 现在是用户对象或错误代码
    # 判断是否为用户对象（成功的情况）
    if isinstance(result, models.User):
        return {
            "code": status.HTTP_200_OK,
            "message": "注册成功",
            "data": {
                "user_id": result.id,
                "username": result.username,
                "phone": result.phone,
                "avatar": result.avatar if result.avatar else ""
            }
        }
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该手机号已注册")
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="注册时发生异常错误")


# 获取账单分类列表
@app.get("/category/list")
def bill_category_list(type: int, db: Session = Depends(database.get_db)):
    if type not in [1, 2]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="type参数输入错误")

    result = crud.category_list(type, db)
    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    else:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "data": result
        }


# 获取支付方式列表
@app.get("/payment_method/list")
def payment_method_list(db: Session = Depends(database.get_db)):
    result = crud.payment_method_list(db)

    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    else:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "data": result
        }


# 创建订单
@app.post("/bill/add")
def bill_add(bill: schemas.bill_add, db: Session = Depends(database.get_db)):
    result = crud.bill_add(bill, db)

    if result == 1:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功"
        }
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该分类不存在")
    elif result == -3:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该支付方式不存在")


# 修改订单
@app.put("/bill/update")
def bill_update(bill: schemas.bill_update, db: Session = Depends(database.get_db)):
    result = crud.bill_update(bill, db)

    if result == 1:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功"
        }
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该分类不存在")
    elif result == -3:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该账单不存在")
    elif result == -4:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该账单不属于此用户")
    elif result == -5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该支付方式不存在")


# 删除账单
@app.delete("/bill/delete")
def bill_delete(bill: schemas.bill_delete, db: Session = Depends(database.get_db)):
    result = crud.bill_delete(bill, db)

    if result == 1:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功"
        }
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该账单不存在")
    elif result == -3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该账单不属于此用户")


# 批量删除账单
@app.delete("/bill/batch-delete")
def bill_batch_delete(payload: schemas.bill_batch_delete, db: Session = Depends(database.get_db)):
    result = crud.bill_batch_delete(payload, db)

    # 成功：返回删除数量（兼容旧风格 code/message）
    if isinstance(result, int) and result > 0:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "deleted_count": result
        }

    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该账单不存在")
    elif result == -3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该账单不属于此用户")
    elif result == -4:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="bill_ids不能为空")

    # 兜底
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="未知错误")


# 获取账单列表
@app.get("/bill/list")
def bill_list(user_id: int, page:int, page_size: int, type: int, the_time: str = None, db: Session = Depends(database.get_db)):
    if page_size <15:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="页面大小太小")
    if type not in [1, 2]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="type参数输入错误")
    
    # 如果传递了 the_time，验证月份是否有效（1-12月）
    if the_time:
        try:
            year_str, month_str = the_time.split('-')
            year = int(year_str)
            month = int(month_str)

            if month < 1 or month > 12:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不正确的日期格式")
    
    temp = crud.get_bill_count(user_id, the_time, page_size, type, db)
    if temp == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif temp == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    total = temp["total"]
    page_num = temp["page_num"]
    if total == 0:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "total": total,
            "page_num": page_num,
            "data": []
        }

    if page < 1 or page > page_num:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="页号输入错误（为负数或是过大）")

    result = crud.bill_list(user_id, the_time, page, page_size, type, db)
    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    else:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
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
            "code": status.HTTP_200_OK,
            "message": "成功"
        }
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="参数输入错误")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不正确的日期格式")
    elif result == -3:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -4:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="总预算还未设置")
    elif result == -5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该分类不存在")
    elif result == -6:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="一个收入分类不能设置预算")
    elif result == -7:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="当月有一个相同分类的预算已经存在")


# 用于删除预算
@app.delete("/budget/delete")
def budget_delete(budget: schemas.budget_delete, db: Session = Depends(database.get_db)):
    result = crud.budget_delete(budget, db)

    if result == 1:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功"
        }
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该预算不存在")
    elif result == -3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该预算不属于此用户")


@app.put("/budget/update")
def budget_update(budget: schemas.budget_update, db: Session = Depends(database.get_db)):
    result = crud.budget_update(budget, db)

    if result == 1:
        return {
            "code": 200,
            "message": "成功"
        }
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该账单不存在")
    elif result == -3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="该预算不属于此用户")


@app.get("/budget/list_month")
def budget_list_month(user_id: int, month: str, db: Session = Depends(database.get_db)):
    result = crud.budget_list_month(user_id, month, db)

    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不正确的日期格式")
    else:
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "data": result
        }


"""
以下是可视化接口部分
"""
# 消费趋势分析之获取近n天数据
@app.get("/analysis/trend/days")
def get_trend_days(user_id: int = Query(..., ge=1),
                days: int = Query(..., ge=7),
                db: Session = Depends(database.get_db)
                ):
    result = crud.get_trend_days(user_id, days, db)

    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    else:
        income_list, expense_list = result
        return {
            "code": status.HTTP_200_OK,
            "message": "success",
            "days": days,
            "data": {
                "income_list": income_list,
                "expense_list": expense_list
            }
        }


# 消费趋势分析之获取近n个月的数据
@app.get("/analysis/trend/months")
def get_trend_months(user_id: int = Query(..., ge=1),
                     months: int = Query(..., ge=3),
                     db: Session = Depends(database.get_db)
                     ):
    result = crud.get_trend_months(user_id, months, db)

    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    else:
        income_list, expense_list = result
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "months": months,
            "data": {
                "income_list": income_list,
                "expense_list": expense_list
            }
        }


# 可视化界面中的“近期账单”
@app.get("/analysis/recent_bills")
def get_recent_bill(user_id: int = Query(..., ge=1),
                    days: int = Query(..., ge=1),
                    db: Session = Depends(database.get_db)
                    ):
    result = crud.get_recent_bills(user_id, days, db)

    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    else:
        return{
            "code": status.HTTP_200_OK,
            "message": "成功",
            "days": days,
            "data": result
        }


# 消费列别占比（单个月，month=-1时为全部，month=0时为当月，month=1时为上个月，以此类推，最多往前推12个月）
@app.get("/analysis/expense_propotion_month")
def get_propotion_month(user_id: int = Query(..., ge=1),
                        month: int = Query(..., ge=-1, le=12),
                        db: Session = Depends(database.get_db)
                        ):
    result = crud.get_propotion_month(user_id, month, db)

    if result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    else:
        time, data = result
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "time": time,
            "data": data
        }