# Docker 部署脚本 (Windows PowerShell)
# 设置错误时停止执行
$ErrorActionPreference = "Stop"

Write-Host "🚀 开始部署 Temu 项目..." -ForegroundColor Green

# 检查 Docker 是否安装
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker 已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker 未安装，请先安装 Docker Desktop" -ForegroundColor Red
    Write-Host "下载地址: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# 检查 Docker Compose 是否安装
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose 已安装: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose 未安装，请先安装 Docker Compose" -ForegroundColor Red
    exit 1
}

# 检查 Docker 服务是否运行
try {
    docker info | Out-Null
    Write-Host "✅ Docker 服务正在运行" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker 服务未运行，请启动 Docker Desktop" -ForegroundColor Red
    exit 1
}

# 创建日志目录
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "📁 创建日志目录" -ForegroundColor Yellow
}

# 停止并删除现有容器
Write-Host "🛑 停止现有容器..." -ForegroundColor Yellow
docker-compose down --remove-orphans

# 清理旧镜像（可选，取消注释以启用）
# Write-Host "🧹 清理旧镜像..." -ForegroundColor Yellow
# docker system prune -f

# 构建镜像
Write-Host "🔨 构建 Docker 镜像..." -ForegroundColor Yellow
docker-compose build

# 启动服务
Write-Host "🚀 启动服务..." -ForegroundColor Yellow
docker-compose up -d

# 等待服务启动
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host "📊 检查服务状态..." -ForegroundColor Yellow
docker-compose ps

# 检查健康状态
Write-Host "🏥 检查健康状态..." -ForegroundColor Yellow
try {
    docker-compose exec -T backend curl -f http://localhost:8000/ | Out-Null
    Write-Host "✅ 后端健康检查通过" -ForegroundColor Green
} catch {
    Write-Host "⚠️  后端健康检查失败" -ForegroundColor Yellow
}

try {
    docker-compose exec -T frontend curl -f http://localhost:80 | Out-Null
    Write-Host "✅ 前端健康检查通过" -ForegroundColor Green
} catch {
    Write-Host "⚠️  前端健康检查失败" -ForegroundColor Yellow
}

Write-Host "`n✅ 部署完成！" -ForegroundColor Green
Write-Host "🌐 前端访问地址: http://localhost:8082" -ForegroundColor Cyan
Write-Host "🔧 后端 API 地址: http://localhost:8082/api" -ForegroundColor Cyan
Write-Host "🔄 统一入口地址: http://localhost:8082" -ForegroundColor Cyan

# 显示日志命令
Write-Host "`n📋 查看日志命令:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f" -ForegroundColor White
Write-Host "  docker-compose logs -f backend" -ForegroundColor White
Write-Host "  docker-compose logs -f frontend" -ForegroundColor White

# 提供停止服务的命令
Write-Host "`n🛑 停止服务命令:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor White

# 可选：自动打开浏览器
$openBrowser = Read-Host "`n是否自动打开浏览器访问应用？(y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "http://localhost:8082"
    Write-Host "🌐 已在浏览器中打开应用" -ForegroundColor Green
} 