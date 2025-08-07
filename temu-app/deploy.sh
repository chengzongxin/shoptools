#!/bin/bash

# Docker 部署脚本
set -e

echo "🚀 开始部署 Temu 项目..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null && ! [ -f /usr/bin/docker ]; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! [ -f /usr/local/bin/docker-compose ]; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查是否有 Docker 权限
if ! docker ps &> /dev/null; then
    echo "⚠️  Docker 权限不足，尝试使用 sudo..."
    # 如果当前用户不在 docker 组中，尝试使用 sudo
    if ! sudo docker ps &> /dev/null; then
        echo "❌ 无法访问 Docker，请确保用户有 Docker 权限或使用 sudo"
        echo "💡 解决方案："
        echo "   1. 将用户添加到 docker 组：sudo usermod -aG docker \$USER"
        echo "   2. 重新登录或重启系统"
        echo "   3. 或者使用 sudo 运行此脚本"
        exit 1
    fi
    # 如果 sudo docker 可用，设置别名
    alias docker="sudo docker"
    alias docker-compose="sudo docker-compose"
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
docker-compose down --remove-orphans

# 清理旧镜像（可选）
echo "🧹 清理旧镜像..."
docker system prune -f

# 构建镜像
echo "🔨 构建 Docker 镜像..."
# docker-compose build --no-cache
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 检查健康状态
echo "🏥 检查健康状态..."
docker-compose exec -T backend curl -f http://localhost:8000/ || echo "⚠️  后端健康检查失败"
docker-compose exec -T frontend curl -f http://localhost:80 || echo "⚠️  前端健康检查失败"

# 初始化数据库（如果需要）
echo "🗄️  检查数据库状态..."
docker-compose exec -T mysql mysql -u root -p123456789 -e "USE temu_app; SHOW TABLES;" || echo "⚠️  数据库检查失败"

echo "✅ 部署完成！"
echo "🌐 前端访问地址: http://localhost:8082"
echo "🔧 后端 API 地址: http://localhost:8082/api"
echo "🔄 统一入口地址: http://localhost:8082"
echo "📊 数据库地址: localhost:3306"

# 显示日志
echo "📋 查看日志命令:"
echo "  docker-compose logs -f"
echo "  docker-compose logs -f backend"
echo "  docker-compose logs -f frontend"
echo "  docker-compose logs -f mysql" 