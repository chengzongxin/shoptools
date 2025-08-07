from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import temu, blue, config, auth, files
from database.connection import engine
from models import user, file_model

# 创建数据库表
user.Base.metadata.create_all(bind=engine)
file_model.Base.metadata.create_all(bind=engine)

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
app.include_router(blue.router, prefix="/api/blue", tags=["蓝站"])
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
