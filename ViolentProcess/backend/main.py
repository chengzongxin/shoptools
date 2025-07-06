"""
TEMU 违规处理工具 - 后端主应用
提供API接口用于处理TEMU违规记录、商品搜索和图片删除功能
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.routers import violations, temu, blue_site, operations
from app.database import init_db

# 创建FastAPI应用实例
app = FastAPI(
    title="TEMU 违规处理工具",
    description="半自动工作流工具，用于处理TEMU违规记录",
    version="1.0.0"
)

# 配置CORS中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React开发服务器端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（用于存储上传的文件）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由模块
app.include_router(violations.router, prefix="/api/violations", tags=["违规记录"])
app.include_router(temu.router, prefix="/api/temu", tags=["TEMU操作"])
app.include_router(blue_site.router, prefix="/api/blue", tags=["图库操作"])
app.include_router(operations.router, prefix="/api/operations", tags=["批量操作"])

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    await init_db()

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "TEMU 违规处理工具 API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # 开发环境运行
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 