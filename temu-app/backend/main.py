from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import temu, config, auth, files
from database.connection import engine
from models import user, file_model, user_config
import os

# 根据环境决定是否自动创建表
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    # 开发环境：自动创建表
    print("🔧 开发环境：自动创建数据库表...")
    user.Base.metadata.create_all(bind=engine)
    file_model.Base.metadata.create_all(bind=engine)
    user_config.Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建完成")
else:
    # 生产环境：依赖 init.sql 初始化
    print("🚀 生产环境：使用 SQL 脚本初始化数据库")

app = FastAPI(title="TEMU工具箱", description="TEMU卖家定制化功能平台", version="1.0.0")

# 允许跨域访问，方便前端本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(temu.router, prefix="/api/temu", tags=["TEMU"])
app.include_router(config.router, prefix="/api", tags=["配置"])
app.include_router(files.router, prefix="/api/files", tags=["文件管理"])

@app.get("/")
def read_root():
    return {"message": "TEMU工具箱后端服务正在运行"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/docs")
def get_docs():
    """API文档地址"""
    return {"docs_url": "/docs", "redoc_url": "/redoc"}
