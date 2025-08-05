# TEMU 定制化功能工具箱

一个专为TEMU卖家设计的定制化功能平台，提供违规商品管理、批量下架、图库搜索等核心功能，帮助卖家高效管理TEMU店铺。

## 🎯 项目概述

本项目是一个前后端分离的Web应用，专门为TEMU卖家提供定制化的店铺管理功能。通过集成TEMU官方API和第三方服务，实现自动化、批量化的商品管理操作，大幅提升卖家的工作效率。

### 核心价值
- **自动化管理**：批量处理违规商品，减少手动操作
- **智能下架**：支持多线程批量下架商品，提高处理效率
- **图库集成**：集成蓝站图库，方便图片资源管理
- **实时监控**：实时获取违规商品信息，及时处理风险

## 🏗️ 技术架构

### 后端技术栈
- **框架**：FastAPI (Python)
- **异步处理**：ThreadPoolExecutor 多线程处理
- **网络请求**：requests + 自定义请求封装
- **数据存储**：JSON配置文件 + 本地缓存
- **API文档**：自动生成OpenAPI文档

### 前端技术栈
- **框架**：React 18 + TypeScript
- **UI组件库**：Ant Design
- **路由管理**：React Router
- **状态管理**：React Context + Hooks
- **构建工具**：Vite
- **开发工具**：Stagewise工具栏

### 部署架构
- **容器化**：Docker + Docker Compose
- **反向代理**：Nginx
- **网络隔离**：Docker Bridge网络
- **健康检查**：容器级健康监控

## 📁 项目结构

```
temu-app/
├── backend/                    # 后端服务
│   ├── main.py                # FastAPI应用入口
│   ├── routers/               # API路由模块
│   │   ├── temu.py           # TEMU相关API
│   │   ├── blue.py           # 蓝站图库API
│   │   └── config.py         # 配置管理API
│   ├── utils/                 # 工具模块
│   │   ├── request.py        # 网络请求封装
│   │   ├── scraper.py        # 数据爬取工具
│   │   └── craw.py           # 违规商品爬虫
│   ├── requirements.txt       # Python依赖
│   └── Dockerfile            # 后端容器配置
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   │   ├── ProductList.tsx      # 违规商品列表
│   │   │   ├── ProductDetail.tsx    # 商品详情
│   │   │   ├── GalleryPage.tsx      # 图库管理
│   │   │   ├── ConfigPage.tsx       # 配置管理
│   │   │   └── UnpublishedRecordsPage.tsx # 未发布记录
│   │   ├── contexts/         # React Context
│   │   ├── types/            # TypeScript类型定义
│   │   └── utils/            # 工具函数
│   ├── package.json          # 前端依赖
│   └── Dockerfile            # 前端容器配置
├── docker-compose.yml         # 容器编排配置
├── nginx-proxy.conf          # Nginx反向代理配置
├── start.sh                  # Linux/Mac启动脚本
├── start.bat                 # Windows启动脚本
└── 启动说明.md               # 详细启动说明
```

## 🚀 核心功能

### 1. 违规商品管理
- **实时获取**：自动爬取TEMU违规商品列表
- **批量操作**：支持批量选择和下架商品
- **智能筛选**：按违规程度、站点等条件筛选
- **详情查看**：查看商品详细信息和违规原因

### 2. 批量商品下架
- **多线程处理**：支持并发批量下架，提高效率
- **智能缓存**：缓存会话信息，减少重复请求
- **状态监控**：实时监控下架进度和结果
- **错误处理**：完善的异常处理和重试机制

### 3. 图库管理
- **蓝站集成**：集成蓝站图库搜索功能
- **图片预览**：支持图片在线预览
- **批量操作**：支持批量删除图片
- **搜索优化**：智能图片名称搜索

### 4. 配置管理
- **多平台配置**：支持TEMU卖家端、合规端、蓝站等多平台配置
- **安全存储**：本地加密存储敏感信息
- **配置验证**：自动验证配置有效性
- **缓存管理**：智能管理API会话缓存

### 5. 未发布记录
- **本地存储**：记录未发布的商品信息
- **状态跟踪**：跟踪商品发布状态
- **批量管理**：支持批量操作未发布商品

## 🔧 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (可选)

### 一键启动

#### Windows用户
```bash
# 双击运行启动脚本
start.bat
```

#### Linux/Mac用户
```bash
# 添加执行权限
chmod +x start.sh stop.sh

# 启动项目
./start.sh
```

### 手动启动

#### 启动后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动前端
```bash
cd frontend
npm install
npm run dev
```

### Docker部署
```bash
# 使用Docker Compose启动
docker-compose up -d

# 访问地址
# 前端: http://localhost:8082
# 后端API: http://localhost:8082/api
```

## 📖 使用指南

### 1. 初始配置
1. 访问配置管理页面
2. 填入各平台的Cookie和Token信息
3. 保存配置并验证连接

### 2. 违规商品处理
1. 进入违规商品列表页面
2. 查看违规商品信息
3. 选择需要下架的商品
4. 点击批量下架按钮
5. 监控下架进度和结果

### 3. 图库管理
1. 进入图库管理页面
2. 输入图片名称进行搜索
3. 查看搜索结果
4. 执行批量删除操作

## 🔒 安全说明

- **本地存储**：所有敏感信息仅存储在本地
- **无云端传输**：不向第三方服务器传输敏感数据
- **配置加密**：本地配置文件采用安全存储方式
- **访问控制**：建议在可信网络环境下使用

## 🛠️ 开发说明

### 后端开发
- 遵循FastAPI最佳实践
- 使用类型注解确保代码质量
- 实现完善的错误处理机制
- 支持异步处理和并发操作

### 前端开发
- 使用TypeScript确保类型安全
- 采用React Hooks和Context管理状态
- 实现响应式设计和用户体验优化
- 支持组件复用和模块化开发

### API设计
- RESTful API设计规范
- 统一的响应格式
- 完善的错误码和错误信息
- 支持分页和筛选查询

## 📝 更新日志

### v1.0.0
- 实现基础违规商品管理功能
- 支持批量商品下架操作
- 集成蓝站图库搜索功能
- 完善配置管理系统
- 支持Docker容器化部署

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关平台的使用条款。

## ⚠️ 免责声明

- 本项目仅用于提高工作效率，请遵守TEMU平台规则
- 使用本工具产生的任何后果由用户自行承担
- 建议在测试环境中充分验证后再用于生产环境

---

**注意**：使用前请确保已获得相关平台的授权，并遵守平台的使用条款和API限制。
