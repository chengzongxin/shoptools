@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 开始部署 Temu 项目...

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('docker --version') do set dockerVersion=%%i
echo ✅ Docker 已安装: !dockerVersion!

REM 检查 Docker Compose 是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('docker-compose --version') do set composeVersion=%%i
echo ✅ Docker Compose 已安装: !composeVersion!

REM 检查 Docker 服务是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 服务未运行，请启动 Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker 服务正在运行

REM 创建日志目录
if not exist "logs" (
    mkdir logs
    echo 📁 创建日志目录
)

REM 停止并删除现有容器
echo 🛑 停止现有容器...
docker-compose down --remove-orphans

REM 清理旧镜像（可选，取消注释以启用）
REM echo 🧹 清理旧镜像...
REM docker system prune -f

REM 构建镜像
echo 🔨 构建 Docker 镜像...
docker-compose build

REM 启动服务
echo 🚀 启动服务...
docker-compose up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose ps

REM 检查健康状态
echo 🏥 检查健康状态...
docker-compose exec -T backend curl -f http://localhost:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端健康检查通过
) else (
    echo ⚠️  后端健康检查失败
)

docker-compose exec -T frontend curl -f http://localhost:80 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 前端健康检查通过
) else (
    echo ⚠️  前端健康检查失败
)

echo.
echo ✅ 部署完成！
echo 🌐 前端访问地址: http://localhost:8082
echo 🔧 后端 API 地址: http://localhost:8082/api
echo 🔄 统一入口地址: http://localhost:8082

REM 显示日志命令
echo.
echo 📋 查看日志命令:
echo   docker-compose logs -f
echo   docker-compose logs -f backend
echo   docker-compose logs -f frontend

REM 提供停止服务的命令
echo.
echo 🛑 停止服务命令:
echo   docker-compose down

REM 可选：自动打开浏览器
set /p openBrowser="是否自动打开浏览器访问应用？(y/n): "
if /i "!openBrowser!"=="y" (
    start http://localhost:8082
    echo 🌐 已在浏览器中打开应用
)

pause 