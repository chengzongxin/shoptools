#!/bin/bash

# Ubuntu 服务器 Docker 部署脚本
set -e

echo "🚀 开始部署 Temu 项目 (Ubuntu 服务器)..."

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  建议使用 root 用户运行此脚本"
    echo "💡 使用命令: sudo su -"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查 Docker 是否安装
echo "🔍 检查 Docker 安装状态..."
if ! command -v docker &> /dev/null && ! [ -f /usr/bin/docker ]; then
    echo "❌ Docker 未安装，正在安装 Docker..."
    
    # 更新包索引
    apt-get update
    
    # 安装必要的包
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # 添加 Docker 官方 GPG 密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 设置稳定版仓库
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装 Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # 启动并启用 Docker
    systemctl start docker
    systemctl enable docker
    
    echo "✅ Docker 安装完成"
else
    echo "✅ Docker 已安装"
fi

# 检查 Docker Compose 是否安装
echo "🔍 检查 Docker Compose 安装状态..."
if ! command -v docker-compose &> /dev/null && ! [ -f /usr/local/bin/docker-compose ]; then
    echo "❌ Docker Compose 未安装，正在安装..."
    
    # 安装 Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    echo "✅ Docker Compose 安装完成"
else
    echo "✅ Docker Compose 已安装"
fi

# 检查 Docker 服务状态
echo "🔍 检查 Docker 服务状态..."
if ! systemctl is-active --quiet docker; then
    echo "⚠️  Docker 服务未运行，正在启动..."
    systemctl start docker
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
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 20

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
echo "🌐 前端访问地址: http://$(curl -s ifconfig.me):8082"
echo "🔧 后端 API 地址: http://$(curl -s ifconfig.me):8082/api"
echo "🔄 统一入口地址: http://$(curl -s ifconfig.me):8082"
echo "📊 数据库地址: localhost:3306"

# 显示日志
echo "📋 查看日志命令:"
echo "  docker-compose logs -f"
echo "  docker-compose logs -f backend"
echo "  docker-compose logs -f frontend"
echo "  docker-compose logs -f mysql"

# 显示防火墙建议
echo "🔒 防火墙配置建议:"
echo "  sudo ufw allow 8082/tcp"
echo "  sudo ufw allow 3306/tcp" 