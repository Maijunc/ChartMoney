from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
import database, models, schemas, crud, security
from dependencies import get_current_user, get_current_user_id
import os
import uuid

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

# 挂载静态文件目录（用于访问上传的头像）
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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


# 更新用户信息
@app.put("/user/update")
def update_user(user_data: schemas.User_update, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    """
    更新当前登录用户的信息（需要 Token）

    请求头需要包含：
    Authorization: Bearer <token>
    """
    result = crud.user_update(current_user.id, user_data, db)

    if isinstance(result, models.User):
        return {
            "code": status.HTTP_200_OK,
            "message": "更新成功",
            "data": {
                "user_id": result.id,
                "username": result.username,
                "phone": result.phone,
                "avatar": result.avatar if result.avatar else ""
            }
        }
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该手机号已被其他用户使用")
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新用户信息时发生异常错误")


# 上传头像
@app.post("/upload/avatar")
async def upload_avatar(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    """
    上传用户头像（需要 Token）

    请求头需要包含：
    Authorization: Bearer <token>
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只支持上传图片文件（jpg, png, gif, webp）")

    # 验证文件大小（限制2MB）
    file_content = await file.read()
    if len(file_content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小不能超过2MB")

    try:
        # 创建上传目录
        upload_dir = "uploads/avatars"
        os.makedirs(upload_dir, exist_ok=True)

        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{current_user.id}_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)

        # 返回文件访问URL（包含完整的服务器地址）
        # 在实际生产环境中，这里应该配置为真实的域名
        avatar_url = f"http://localhost:8000/uploads/avatars/{unique_filename}"

        return {
            "code": status.HTTP_200_OK,
            "message": "头像上传成功",
            "data": {
                "url": avatar_url,
                "filename": unique_filename
            }
        }
    except Exception as e:
        print(f"上传头像失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="上传头像时发生错误")


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

    # 修复：检查是否返回了Budget对象（成功情况）
    if isinstance(result, models.Budget):
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "data": {
                "id": result.id,
                "user_id": result.user_id,
                "category_id": result.category_id,
                "is_total": result.is_total,
                "amount": float(result.amount),
                "month": result.month
            }
        }
    # 以下处理错误情况（当result为整数时）
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

    # 修复：检查是否返回了Budget对象（成功情况）
    if isinstance(result, models.Budget):
        return {
            "code": status.HTTP_200_OK,
            "message": "成功",
            "data": {
                "id": result.id,
                "user_id": result.user_id,
                "category_id": result.category_id,
                "is_total": result.is_total,
                "amount": float(result.amount),
                "month": result.month
            }
        }
    # 以下处理错误情况（当result为整数时）
    elif result == 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="进行数据库业务时出错")
    elif result == -1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该用户不存在")
    elif result == -2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="该预算不存在")
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
                        month: int = Query(..., ge=-1, le=11),
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


# 导出用户数据（包括账单、预算等）
@app.get("/user/export")
def export_user_data(user_id: int = Query(..., ge=1), db: Session = Depends(database.get_db)):
    """
    导出用户的所有财务数据
    """
    # 验证用户是否存在
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    try:
        # 获取所有账单
        bills_result = db.execute(
            select(models.Bill)
            .where(models.Bill.user_id == user_id)
            .order_by(models.Bill.bill_time.desc())
        )
        bills = bills_result.scalars().all()

        # 获取所有预算
        budgets_result = db.execute(
            select(models.Budget)
            .where(models.Budget.user_id == user_id)
        )
        budgets = budgets_result.scalars().all()

        # 构建导出数据
        export_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "phone": user.phone,
                "avatar": user.avatar or ""
            },
            "bills": [
                {
                    "id": bill.id,
                    "name": bill.name,
                    "amount": float(bill.amount),
                    "category_id": bill.category_id,
                    "method_id": bill.method_id,
                    "bill_time": bill.bill_time.isoformat() if bill.bill_time else None,
                    "remark": bill.remark or ""
                }
                for bill in bills
            ],
            "budgets": [
                {
                    "id": budget.id,
                    "category_id": budget.category_id,
                    "amount": float(budget.amount),
                    "month": budget.month,
                    "is_total": budget.is_total
                }
                for budget in budgets
            ],
            "export_time": datetime.now().isoformat(),
            "total_bills": len(bills),
            "total_budgets": len(budgets)
        }

        return {
            "code": status.HTTP_200_OK,
            "message": "数据导出成功",
            "data": export_data
        }
    except Exception as e:
        print(f"导出数据失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="导出数据时发生错误")


# 清理过期数据
@app.delete("/user/clear-expired")
def clear_expired_data(payload: dict, db: Session = Depends(database.get_db)):
    """
    清理指定天数之前的账单数据
    """
    user_id = payload.get("user_id")
    days = payload.get("days", 365)

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id 不能为空")

    # 验证用户是否存在
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    try:
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=days)

        # 删除过期账单
        delete_stmt = delete(models.Bill).where(
            models.Bill.user_id == user_id,
            models.Bill.bill_time < cutoff_date
        )
        result = db.execute(delete_stmt)
        deleted_count = result.rowcount

        db.commit()

        return {
            "code": status.HTTP_200_OK,
            "message": f"已清理 {deleted_count} 条过期账单",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        print(f"清理过期数据失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="清理数据时发生错误")


# 清空所有数据
@app.delete("/user/clear-all")
def clear_all_data(payload: dict, db: Session = Depends(database.get_db)):
    """
    清空用户的所有账单和预算数据
    """
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id 不能为空")

    # 验证用户是否存在
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    try:
        # 删除所有账单
        bills_delete_stmt = delete(models.Bill).where(models.Bill.user_id == user_id)
        bills_result = db.execute(bills_delete_stmt)
        bills_count = bills_result.rowcount

        # 删除所有预算
        budgets_delete_stmt = delete(models.Budget).where(models.Budget.user_id == user_id)
        budgets_result = db.execute(budgets_delete_stmt)
        budgets_count = budgets_result.rowcount

        db.commit()

        return {
            "code": status.HTTP_200_OK,
            "message": f"已清空所有数据（{bills_count} 条账单，{budgets_count} 条预算）",
            "deleted_bills": bills_count,
            "deleted_budgets": budgets_count
        }
    except Exception as e:
        db.rollback()
        print(f"清空数据失败: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="清空数据时发生错误")


