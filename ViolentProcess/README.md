# TEMU 违规处理工具

一个半自动的工作流工具，用于处理TEMU违规记录，包括商品搜索、下架处理和图片删除功能。

## 项目结构

```
temu-toolkit/
├── frontend/                 # React 前端项目
│   ├── src/
│   │   ├── components/       # React组件
│   │   ├── services/         # API服务
│   │   └── utils/           # 工具函数
│   └── package.json
├── backend/                  # FastAPI 后端项目
│   ├── app/
│   │   ├── routers/         # API路由
│   │   ├── services/        # 业务逻辑
│   │   ├── models/          # 数据模型
│   │   └── utils/           # 工具函数
│   ├── requirements.txt
│   └── main.py
├── data/                     # 数据存储
└── .env                      # 环境变量
```

## 技术栈

- **前端**: React + Vite + Axios
- **后端**: Python FastAPI
- **爬虫**: requests + BeautifulSoup
- **数据存储**: SQLite + JSON

## 快速开始

### 1. 后端启动
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 3. 配置环境变量
复制 `.env.example` 为 `.env` 并填入相应的Cookie信息。

## 功能特性

- 🔍 违规记录搜索和展示
- 🛒 TEMU商品搜索和下架
- 🖼️ 图库图片搜索和删除
- 📊 批量处理和历史记录
- 🔐 Cookie管理和登录状态
- 📝 操作日志和结果导出 