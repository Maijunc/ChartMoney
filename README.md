# ChartMoney
"查特猫" A personal financial management and visual analysis system

**致团队成员：** 请务必按照以下步骤配置开发环境。如果有报错，请先截图发群里，不要自己闷头改配置。

## 🛠️ 0. 环境准备 (所有人都必须安装)

在开始之前，请确保你的电脑安装了以下软件：

1. **Git:** [下载地址](https://www.google.com/search?q=https://git-scm.com/downloads) (用于代码同步)
2. **Python 3.9+:** [下载地址](https://www.python.org/downloads/) (后端语言)
   - *注意：安装时务必勾选 "Add Python to PATH"*
3. **Node.js (LTS版本):** [下载地址](https://nodejs.org/zh-cn/) (前端运行环境)
4. **MySQL 8.0+:** (数据库)
   - 推荐安装 Navicat 或 DBeaver 作为可视化客户端。

------

## 🚀 1. 项目初始化 (只做一次)

打开终端 (CMD / PowerShell / Terminal)，执行以下命令：

Bash

```
# 1. 克隆项目 (换成咱们仓库的地址)
git clone https://github.com/你的用户名/仓库名.git

# 2. 进入项目目录
cd finance-project
```

------

## 🐍 2. 后端启动指南 (FastAPI)

后端代码都在 `backend` 目录下。

### 第一次运行配置：

Bash

```
cd backend

# 1. 创建虚拟环境 (防止依赖冲突)
python -m venv venv

# 2. 激活虚拟环境 (关键步骤！)
# Windows系统执行:
venv\Scripts\activate
# Mac/Linux系统执行:
# source venv/bin/activate
# (激活成功后，命令行前面会出现 (venv) 字样)

# 3. 安装依赖包
pip install -r requirements.txt
```

### 数据库配置：

1. 打开你的 MySQL 客户端，创建一个空数据库，名字叫 `finance_db`。

2. 打开代码文件 `backend/database.py`。

3. 修改 `SQLALCHEMY_DATABASE_URL` 这一行，填入你自己的数据库密码：

   Python

   ```
   # 格式: mysql+pymysql://root:你的密码@localhost:3306/finance_db
   ```

### 启动后端：

确保虚拟环境已激活 `(venv)`，在 `backend` 目录下运行：

Bash

```
uvicorn main:app --reload
```

- 看见 `Uvicorn running on http://127.0.0.1:8000` 即为成功。