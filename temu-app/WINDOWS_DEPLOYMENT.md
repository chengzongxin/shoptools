# Windows 平台部署说明

本文档介绍如何在 Windows 平台上部署 Temu 项目。

## 前置要求

### 1. 安装 Docker Desktop
- 下载地址：https://www.docker.com/products/docker-desktop
- 安装完成后启动 Docker Desktop
- 确保 Docker 服务正在运行

### 2. 验证安装
打开命令提示符或 PowerShell，运行以下命令验证：
```bash
docker --version
docker-compose --version
docker info
```

## 部署方式

### 方式一：使用 PowerShell 脚本（推荐）

1. **右键点击 `deploy.ps1` 文件**
2. **选择"使用 PowerShell 运行"**

或者：

1. **打开 PowerShell**
2. **导航到项目目录**
3. **运行脚本**：
   ```powershell
   .\deploy.ps1
   ```

### 方式二：使用批处理脚本

1. **双击 `deploy.bat` 文件**

或者：

1. **打开命令提示符**
2. **导航到项目目录**
3. **运行脚本**：
   ```cmd
   deploy.bat
   ```

## 脚本功能说明

### 检查项目
- ✅ 检查 Docker 是否安装
- ✅ 检查 Docker Compose 是否安装
- ✅ 检查 Docker 服务是否运行
- ✅ 显示版本信息

### 部署流程
- 🛑 停止现有容器
- 🔨 构建 Docker 镜像
- 🚀 启动服务
- ⏳ 等待服务启动
- 📊 检查服务状态
- 🏥 健康检查

### 部署结果
- ✅ 显示访问地址
- 📋 提供日志查看命令
- 🛑 提供停止服务命令
- 🌐 可选自动打开浏览器

## 访问地址

部署成功后，可以通过以下地址访问：

- **前端界面**：http://localhost:8082
- **后端 API**：http://localhost:8082/api
- **统一入口**：http://localhost:8082

## 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

## 故障排除

### 1. PowerShell 执行策略问题
如果遇到执行策略错误，运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Docker 服务未启动
- 检查 Docker Desktop 是否已启动
- 在系统托盘中找到 Docker 图标，确保状态为运行中

### 3. 端口被占用
如果 8082 端口被占用，可以修改 `docker-compose.yml` 中的端口配置：
```yaml
ports:
  - "${NGINX_PORT:-8083}:80"  # 改为 8083 或其他端口
```

### 4. 构建失败
- 检查网络连接
- 清理 Docker 缓存：`docker system prune -f`
- 重新构建：`docker-compose build --no-cache`

## 注意事项

1. **首次运行**：首次部署可能需要较长时间，因为需要下载和构建镜像
2. **防火墙**：确保 Windows 防火墙允许 Docker 访问网络
3. **权限**：确保以管理员身份运行脚本（如果需要）
4. **磁盘空间**：确保有足够的磁盘空间用于 Docker 镜像

## 环境变量配置

可以通过环境变量自定义配置：

- `NGINX_PORT`：Nginx 代理端口（默认：8082）
- `BACKEND_PORT`：后端服务端口（默认：8000）
- `FRONTEND_PORT`：前端服务端口（默认：80）

在运行脚本前设置环境变量：
```cmd
set NGINX_PORT=8083
deploy.bat
```

或在 PowerShell 中：
```powershell
$env:NGINX_PORT=8083
.\deploy.ps1
``` 