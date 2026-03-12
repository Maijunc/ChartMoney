# ChartMoney (查特猫) - 个人记账与可视化分析系统

本项目分为 FastAPI 后端与 Vue3 前端两部分。为了能够顺利运行和体验完整功能，请按照以下步骤依次启动。

## 目录结构
* `finance-project/backend`: 后端服务 (FastAPI)
* `finance-project/frontend`: 前端展示 (Vue3 + Vite)

---

## 1. 基础环境准备
在开始之前，请确保本地已安装以下基础环境：
* **Anaconda / Miniconda** (用于配置 Python 隔离环境)
* **Node.js** (v20 及以上，用于启动前端)
* **MySQL** (v8.0 及以上)

**准备数据库：** 请提前在本地 MySQL 中创建一个空的数据库，命名为 `finance_db`。

---

## 2. 后端服务部署

请打开终端，进入后端目录：
`cd finance-project/backend`

### 2.1 配置 Python 虚拟环境
强烈建议使用 conda 创建独立的虚拟环境，以避免与其他项目冲突：
`conda create -n chartmoney python=3.12.7 -y`
`conda activate chartmoney`

### 2.2 安装依赖包
执行以下命令安装项目所需依赖：
`pip install -r requirements.txt`

> **提示：** 由于开发时使用了基础的 conda 环境，如果后续启动时提示 `ModuleNotFoundError`（找不到某些模块），请直接通过 `pip install <缺失的包名>` 进行快速补充。

### 2.3 配置数据库连接
打开 `finance-project/backend/database.py` 文件，找到数据库连接配置行，将账号密码修改为你本机的 MySQL 配置：
`ASYNC_SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:你的密码@127.0.0.1:3306/finance_db"`

### 2.4 初始化数据库与测试数据（必做）
为了方便快速体验项目，我们提供了一键初始化脚本。该脚本会自动创建所需的数据库表，并写入演示用的流水数据。
请在后端目录下运行：
`python init_database.py`

**注意：** 脚本运行成功后，终端会打印出分配给你的**测试账号和密码**（例如：`testuser / 123456`）。请务必留意并保存，稍后在前端页面需要使用该账号登录。

### 2.5 启动后端
环境和数据准备就绪后，启动 FastAPI 后端服务：
`uvicorn main:app --reload`

后端启动后，可以通过浏览器访问接口文档来验证服务是否正常运行：
* Swagger 接口文档：http://127.0.0.1:8000/docs

---

## 3. 前端服务部署

请**新开一个终端窗口**（保持后端终端继续运行），进入前端目录：
`cd finance-project/frontend`

安装前端依赖库：
`npm install`

启动前端开发服务器：
`npm run dev`

启动成功后，在浏览器中访问控制台提供的本地地址（通常为）：
* http://localhost:5173

打开网页后，输入第 2.4 步中获取的**测试账号和密码**即可登录体验系统。

---

## 4. 补充配置（可选）：短信验证码
本项目集成了阿里云的短信验证码功能。如果不测试找回密码/短信登录等功能，可直接跳过此步。

如需完整体验，后端会读取 `finance-project/backend/.env` 文件中的配置，请在根目录下新建 `.env` 文件并填入您自己的阿里云参数：
* ALIBABA_CLOUD_ACCESS_KEY_ID
* ALIBABA_CLOUD_ACCESS_KEY_SECRET
* ALIBABA_CLOUD_SMS_TEMPLATE_CODE1
* ALIBABA_CLOUD_SMS_TEMPLATE_PARAMS
* ALIBABA_CLOUD_SMS_TEMPLATE_CODE5