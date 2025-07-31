# WebSocket Cookie获取功能说明

## 功能介绍

WebSocket Cookie获取功能允许通过Chrome浏览器插件直接获取当前浏览器中的Cookie，避免了手动复制粘贴的繁琐过程。

## 使用前准备

### 1. 安装依赖

确保已安装 `websockets` 依赖：

```bash
pip install websockets>=12.0
```

### 2. Chrome插件要求

需要安装配套的Chrome插件，插件应该：

- 连接到 `ws://localhost:8765` WebSocket服务器
- 支持响应 `get_cookies_by_domain` 命令
- 返回指定域名的Cookie列表

## 使用方法

### 1. 启动程序

程序启动时会自动启动WebSocket服务器，您会在日志中看到：

```
WebSocket服务器已启动 (ws://localhost:8765)
```

### 2. 连接Chrome插件

- 在Chrome浏览器中启用配套插件
- 插件会自动连接到WebSocket服务器
- 连接成功后可以在服务器日志中看到连接信息

### 3. 获取Cookie

在"系统配置"标签页中：

1. 点击 **"获取Cookie(插件)"** 按钮
2. 程序会向Chrome插件发送获取Cookie的命令
3. 插件返回TEMU网站的Cookie
4. Cookie会自动填入文本框中

## 插件通信协议

### 命令格式

发送给插件的命令格式：

```json
{
    "type": "backend_command",
    "command": "get_cookies_by_domain",
    "params": {
        "domain": "agentseller.temu.com"
    },
    "command_id": "cmd_1234567890"
}
```

### 响应格式

插件应该返回的响应格式：

```json
{
    "type": "command_response",
    "data": {
        "success": true,
        "cookies": [
            {
                "name": "cookie_name",
                "value": "cookie_value"
            }
        ]
    }
}
```

## 故障排除

### 1. "没有连接的Chrome插件"

**原因：** Chrome插件未连接到WebSocket服务器

**解决方法：**
- 检查Chrome插件是否已安装并启用
- 确认插件连接的WebSocket地址是 `ws://localhost:8765`
- 检查防火墙是否阻止了本地连接

### 2. "WebSocket获取Cookie失败"

**原因：** 插件响应超时或格式错误

**解决方法：**
- 检查插件是否正常工作
- 确认插件返回的数据格式正确
- 检查浏览器是否已登录TEMU网站

### 3. "WebSocket服务器启动失败"

**原因：** 端口被占用或权限不足

**解决方法：**
- 检查端口8765是否被其他程序占用
- 尝试以管理员权限运行程序
- 检查防火墙设置

## 技术细节

### WebSocket服务器

- **地址：** `ws://localhost:8765`
- **协议：** WebSocket
- **超时时间：** 10秒

### 线程安全

所有GUI操作都通过 `self.after()` 方法调度到主线程执行，确保线程安全。

### 错误处理

- 连接失败时会回退到浏览器Cookie获取方式
- 所有异常都会被捕获并显示用户友好的错误信息
- 支持超时处理，避免程序假死

## 开发者信息

如需开发配套的Chrome插件，请参考以下资源：

- [Chrome Extension API文档](https://developer.chrome.com/docs/extensions/)
- [WebSocket API文档](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Cookie API文档](https://developer.chrome.com/docs/extensions/reference/cookies/)