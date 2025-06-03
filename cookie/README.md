# Chrome扩展开发模板

这是一个使用React + TypeScript开发Chrome扩展的模板项目。该项目提供了一个获取网页Cookie的Chrome扩展示例，可以作为开发其他Chrome扩展的基础模板。

## 项目结构

```
cookie/
├── src/                    # 源代码目录
│   ├── popup.tsx          # 弹出窗口组件
│   └── background.ts      # 后台脚本
├── public/                # 静态资源目录
│   ├── manifest.json      # 扩展配置文件
│   └── popup.html        # 弹出窗口HTML
├── dist/                  # 构建输出目录
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript配置
└── vite.config.ts         # Vite配置
```

## 开发环境要求

- Node.js (推荐 v16+)
- npm 或 yarn
- Chrome浏览器

## 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd [项目目录]
```

2. 安装依赖
```bash
npm install
```

## 开发流程

### 1. 启动开发环境

需要同时运行两个命令：

```bash
# 终端1：启动开发服务器
npm run dev

# 终端2：启动监视模式
npm run watch
```

### 2. 在Chrome中加载扩展

1. 打开Chrome浏览器
2. 访问 `chrome://extensions/`
3. 开启右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择项目的 `dist` 目录

### 3. 开发工作流程

1. 修改代码
2. 保存文件
3. 在Chrome扩展管理页面点击刷新按钮
4. 查看变化

## 调试技巧

### 1. 查看后台脚本日志

1. 在Chrome扩展管理页面
2. 找到你的扩展
3. 点击"Service Worker"链接
4. 查看控制台输出

### 2. 查看弹出窗口日志

1. 右键点击扩展图标
2. 选择"检查弹出内容"
3. 查看控制台输出

## 构建项目

```bash
npm run build
```

构建后的文件会在 `dist` 目录中。

## 项目配置说明

### manifest.json

```json
{
  "manifest_version": 3,
  "name": "扩展名称",
  "version": "1.0",
  "description": "扩展描述",
  "permissions": [
    "cookies",
    "activeTab"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "action": {
    "default_popup": "popup.html"
  },
  "background": {
    "service_worker": "background.js",
    "type": "module"
  }
}
```

### package.json 脚本说明

- `npm run dev`: 启动开发服务器
- `npm run build`: 构建项目
- `npm run watch`: 监视模式
- `npm run preview`: 预览构建结果

## 开发新扩展的步骤

1. **创建项目结构**
   - 复制模板项目
   - 修改项目名称和描述
   - 更新依赖

2. **配置manifest.json**
   - 设置扩展名称和描述
   - 配置所需权限
   - 设置入口文件

3. **开发功能**
   - 在 `src` 目录下开发
   - 使用TypeScript编写代码
   - 使用React开发界面

4. **测试和调试**
   - 使用开发模式测试
   - 使用Chrome开发者工具调试
   - 检查控制台输出

5. **构建和发布**
   - 运行构建命令
   - 测试构建结果
   - 准备发布材料

## 常用Chrome API

### 1. 标签页API
```typescript
// 获取当前标签页
const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
```

### 2. Cookie API
```typescript
// 获取所有cookie
const cookies = await chrome.cookies.getAll({ url });
```

### 3. 存储API
```typescript
// 存储数据
await chrome.storage.local.set({ key: value });

// 读取数据
const data = await chrome.storage.local.get(['key']);
```

## 注意事项

1. **权限管理**
   - 只请求必要的权限
   - 在manifest.json中声明权限
   - 注意权限范围

2. **性能优化**
   - 减少不必要的API调用
   - 优化代码结构
   - 注意内存使用

3. **安全考虑**
   - 注意数据安全
   - 验证用户输入
   - 保护敏感信息

4. **调试技巧**
   - 使用console.log输出调试信息
   - 使用Chrome开发者工具
   - 使用断点调试

## 常见问题解决

1. **扩展不显示**
   - 检查manifest.json配置
   - 确认构建成功
   - 检查权限设置

2. **API调用失败**
   - 检查权限声明
   - 确认API使用正确
   - 查看错误信息

3. **构建错误**
   - 检查TypeScript配置
   - 确认依赖安装
   - 查看构建日志

## 参考资源

- [Chrome扩展开发文档](https://developer.chrome.com/docs/extensions/)
- [Chrome API文档](https://developer.chrome.com/docs/extensions/reference/)
- [React文档](https://reactjs.org/)
- [TypeScript文档](https://www.typescriptlang.org/)
- [Vite文档](https://vitejs.dev/)

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License 