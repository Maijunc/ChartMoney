"""
数据库初始化脚本
用于创建表结构并插入测试数据
"""
import asyncio
from database import engine, AsyncSessionLocal
from models import Base, User, Bill_Category, Payment_Method, Bill, Budget
from datetime import datetime, timedelta
import security
import random


async def init_database():
    """初始化数据库：删除旧表，创建新表，插入测试数据"""

    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60)

    # 1. 删除所有旧表（谨慎操作！）
    print("\n[1/6] 删除旧表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("旧表已删除")

    # 2. 创建所有新表
    print("\n[2/6] 创建新表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("新表已创建")

    # 3. 获取数据库会话
    async with AsyncSessionLocal() as db:
        try:
            # 4. 插入测试用户
            print("\n[3/6] 插入测试用户...")
            test_users = [
                User(
                    username="testuser",
                    password=security.hash_password("123456"),
                    phone="13800138000"
                ),
                User(
                    username="admin",
                    password=security.hash_password("admin123"),
                    phone="13800138001"
                ),
                User(
                    username="demo",
                    password=security.hash_password("demo123"),
                    phone="13800138002"
                )
            ]
            db.add_all(test_users)
            await db.commit()
            print(f"已创建 {len(test_users)} 个测试用户")
            print(f"   - testuser / 123456 (手机: 13800138000)")
            print(f"   - admin / admin123 (手机: 13800138001)")
            print(f"   - demo / demo123 (手机: 13800138002)")

            # 5. 插入账单分类
            print("\n[4/6] 插入账单分类...")
            categories = [
                # 收入分类 (type=1)
                Bill_Category(name="工资", type=1),
                Bill_Category(name="奖金", type=1),
                Bill_Category(name="理财收益", type=1),
                Bill_Category(name="兼职收入", type=1),
                Bill_Category(name="其他收入", type=1),

                # 支出分类 (type=2)
                Bill_Category(name="餐饮美食", type=2),
                Bill_Category(name="交通出行", type=2),
                Bill_Category(name="居住房租", type=2),
                Bill_Category(name="购物消费", type=2),
                Bill_Category(name="休闲娱乐", type=2),
                Bill_Category(name="医疗健康", type=2),
                Bill_Category(name="学习教育", type=2),
                Bill_Category(name="人情往来", type=2),
                Bill_Category(name="其他支出", type=2),
            ]
            db.add_all(categories)
            await db.commit()
            print(f"已创建 {len(categories)} 个分类")
            print(f"   - 收入分类: 5个")
            print(f"   - 支出分类: 9个")

            # 6. 插入支付方式
            print("\n[5/6] 插入支付方式...")
            payment_methods = [
                Payment_Method(name="微信"),
                Payment_Method(name="支付宝"),
                Payment_Method(name="现金"),
                Payment_Method(name="银行卡"),
                Payment_Method(name="信用卡"),
            ]
            db.add_all(payment_methods)
            await db.commit()
            print(f"已创建 {len(payment_methods)} 个支付方式")

            # 7. 为 testuser 插入测试账单数据
            print("\n[6/6] 为 testuser 插入测试账单数据...")

            # 获取分类ID
            income_categories = [cat for cat in categories if cat.type == 1]
            expense_categories = [cat for cat in categories if cat.type == 2]

            # 生成近3个月的账单数据
            bills = []
            bill_count = 0

            # 收入数据（每月2-3笔）
            for month_offset in range(3):
                current_date = datetime.now() - timedelta(days=30 * month_offset)

                # 工资收入
                bills.append(Bill(
                    user_id=1,  # testuser
                    category_id=income_categories[0].id,  # 工资
                    method_id=payment_methods[0].id,  # 微信
                    name="月度工资",
                    amount=8000.00,
                    remark="公司发放",
                    bill_time=current_date.replace(day=5, hour=10, minute=0, second=0)
                ))
                bill_count += 1

                # 偶尔有奖金
                if month_offset == 0:
                    bills.append(Bill(
                        user_id=1,
                        category_id=income_categories[1].id,  # 奖金
                        method_id=payment_methods[3].id,  # 银行卡
                        name="绩效奖金",
                        amount=2000.00,
                        remark="Q4绩效",
                        bill_time=current_date.replace(day=15, hour=14, minute=30, second=0)
                    ))
                    bill_count += 1

            # 支出数据（每月15-20笔）
            expense_names = {
                "餐饮美食": ["午餐", "晚餐", "早餐", "下午茶", "聚餐", "外卖"],
                "交通出行": ["地铁费", "打车", "公交卡充值", "加油", "停车费"],
                "居住房租": ["房租", "物业费", "水费", "电费", "网费"],
                "购物消费": ["衣服", "鞋子", "日用品", "化妆品", "电子产品"],
                "休闲娱乐": ["电影票", "KTV", "健身房", "游戏充值", "旅游"],
                "医疗健康": ["买药", "体检", "看病", "保健品"],
                "学习教育": ["书籍", "网课", "培训费"],
                "人情往来": ["礼物", "红包", "聚会"],
            }

            for month_offset in range(3):
                base_date = datetime.now() - timedelta(days=30 * month_offset)

                # 每月生成 15-20 笔支出
                for _ in range(random.randint(15, 20)):
                    # 随机选择支出分类
                    category = random.choice(expense_categories[:-1])  # 排除"其他支出"
                    category_name = category.name

                    # 随机选择账单名称
                    if category_name in expense_names:
                        bill_name = random.choice(expense_names[category_name])
                    else:
                        bill_name = category_name

                    # 随机金额
                    if category_name == "居住房租":
                        amount = random.uniform(1000, 3000)
                    elif category_name == "购物消费":
                        amount = random.uniform(100, 1000)
                    elif category_name == "餐饮美食":
                        amount = random.uniform(10, 200)
                    elif category_name == "交通出行":
                        amount = random.uniform(5, 100)
                    else:
                        amount = random.uniform(20, 500)

                    # 随机日期（当月1-28号）
                    day = random.randint(1, 28)
                    hour = random.randint(8, 22)
                    minute = random.randint(0, 59)

                    bills.append(Bill(
                        user_id=1,
                        category_id=category.id,
                        method_id=random.choice(payment_methods).id,
                        name=bill_name,
                        amount=round(amount, 2),
                        remark=random.choice(["", "必要开支", "冲动消费", "计划内"]),
                        bill_time=base_date.replace(day=day, hour=hour, minute=minute, second=0)
                    ))
                    bill_count += 1

            db.add_all(bills)
            await db.commit()
            print(f"已为 testuser 创建 {bill_count} 笔账单")

            # 8. 为 testuser 插入预算数据
            print("\n[7/7] 为 testuser 插入预算数据...")
            current_month = datetime.now().strftime("%Y-%m")
            budgets = [
                # 月度总预算
                Budget(
                    user_id=1,
                    category_id=None,
                    is_total=True,
                    amount=5000.00,
                    month=current_month
                ),
                # 餐饮预算
                Budget(
                    user_id=1,
                    category_id=expense_categories[0].id,  # 餐饮美食
                    is_total=False,
                    amount=1500.00,
                    month=current_month
                ),
                # 交通预算
                Budget(
                    user_id=1,
                    category_id=expense_categories[1].id,  # 交通出行
                    is_total=False,
                    amount=500.00,
                    month=current_month
                ),
            ]
            db.add_all(budgets)
            await db.commit()
            print(f"已为 testuser 创建 {len(budgets)} 个预算")

            print("\n" + "=" * 60)
            print("数据库初始化完成！")
            print("=" * 60)
            print("\n数据统计:")
            print(f"  - 用户数: {len(test_users)}")
            print(f"  - 分类数: {len(categories)}")
            print(f"  - 支付方式: {len(payment_methods)}")
            print(f"  - 账单数: {bill_count}")
            print(f"  - 预算数: {len(budgets)}")

            print("\n测试账号:")
            print("  用户名: testuser")
            print("  密码: 123456")
            print("  手机: 13800138000")

            print("\n下一步:")
            print("  1. 启动后端: uvicorn main:app --reload")
            print("  2. 启动前端: npm run dev")
            print("  3. 使用 testuser 登录查看数据")
            print("\n")

        except Exception as e:
            print(f"\n错误: {e}")
            await db.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
