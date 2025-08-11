#!/bin/bash

# 开发环境 Docker 部署脚本
set -e

echo "🚀 开始部署 Temu 项目（开发环境）..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p backend/uploads

# 设置文件权限
echo "🔐 设置文件权限..."
chmod 755 backend/uploads

# 停止并删除现有容器
echo "🛑 停止现有容器..."
docker-compose -f docker-compose.dev.yml down --remove-orphans

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose -f docker-compose.dev.yml build

# 启动服务
echo "🚀 启动服务..."
docker-compose -f docker-compose.dev.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose.dev.yml ps

# 检查健康状态
echo "🏥 检查健康状态..."
docker-compose -f docker-compose.dev.yml exec -T backend curl -f http://localhost:8000/ || echo "⚠️  后端健康检查失败"
docker-compose -f docker-compose.dev.yml exec -T frontend curl -f http://localhost:80 || echo "⚠️  前端健康检查失败"

echo "✅ 开发环境部署完成！"
echo "🌐 前端访问地址: http://localhost:5173"
echo "🔧 后端 API 地址: http://localhost:8000"
echo "📊 数据库地址: localhost:3306"
echo "📚 API 文档地址: http://localhost:8000/docs"

# 显示日志
echo "📋 查看日志命令:"
echo "  docker-compose -f docker-compose.dev.yml logs -f"
echo "  docker-compose -f docker-compose.dev.yml logs -f backend"
echo "  docker-compose -f docker-compose.dev.yml logs -f frontend" 