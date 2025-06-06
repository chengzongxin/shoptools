# Temu卖家自动化工具

这是一个用于 Temu 卖家自动化工作流程的工具，支持价格审核和合规审核功能。

## 功能特点

- 价格审核：自动检查商品价格
- 合规审核：自动检查商品合规性
- 支持自定义浏览器调试端口
- 详细的日志记录
- 灵活的运行模式选择

## 系统要求

- Node.js 16.0 或更高版本
- Chrome 或 Chromium 浏览器
- npm 或 yarn 包管理器

## 完整使用流程

### 1. 开发者发布流程

1. **准备发布**
   ```bash
   # 确保代码已提交
   git add .
   git commit -m "准备发布"
   
   # 更新版本号
   npm version patch  # 小版本更新
   ```

2. **发布到 npm**
   ```bash
   # 登录 npm（如果还没有登录）
   npm login
   
   # 发布包
   npm publish
   ```

### 2. 用户安装和使用流程

#### Windows 用户

1. **安装**
   ```bash
   # 以管理员身份运行 PowerShell 或命令提示符
   npm install -g temu-seller-automation
   ```

2. **启动浏览器**
   ```bash
   # 创建配置目录
   mkdir C:\selenium\ChromeProfile
   
   # 启动 Chrome
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\ChromeProfile"
   ```

3. **使用工具**
   ```bash
   # 运行价格审核
   temu-auto --price
   
   # 运行合规审核
   temu-auto --compliance
   ```

#### macOS 用户

1. **安装**
   ```bash
   # 使用 sudo 安装
   sudo npm install -g temu-seller-automation
   ```

2. **启动浏览器**
   ```bash
   # 创建配置目录
   mkdir -p ~/selenium/ChromeProfile
   
   # 启动 Chrome
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/selenium/ChromeProfile"
   ```

3. **使用工具**
   ```bash
   # 运行价格审核
   temu-auto --price
   
   # 运行合规审核
   temu-auto --compliance
   ```

### 3. 常见问题解决

1. **命令不可用**
   - 检查安装：`npm list -g temu-seller-automation`
   - 检查环境变量：`echo %PATH%` 或 `echo $PATH`
   - 重新安装：`npm uninstall -g temu-seller-automation && npm install -g temu-seller-automation`

2. **权限问题**
   - Windows：以管理员身份运行
   - macOS/Linux：使用 `sudo`

3. **浏览器连接问题**
   - 确保浏览器已启动
   - 检查端口号
   - 检查端口占用

## 安装

### 全局安装（推荐）

```bash
# 安装最新版本
npm install -g temu-seller-automation

# 安装特定版本
npm install -g temu-seller-automation@1.0.0
```

### 本地开发安装

```bash
# 克隆仓库
git clone [仓库地址]

# 进入项目目录
cd temu-seller-automation

# 安装依赖
npm install
```

## 使用方法

### 全局命令行使用

安装后，可以直接使用 `temu-auto` 命令：

```bash
# 运行所有功能
temu-auto

# 运行价格审核
temu-auto --price

# 运行合规审核
temu-auto --compliance

# 使用指定端口
temu-auto --port=9223

# 查看帮助信息
temu-auto --help
```

### 启动浏览器

在运行程序之前，需要先启动 Chrome 浏览器：

#### Windows
```bash
# 创建配置目录
mkdir C:\selenium\ChromeProfile

# 启动 Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\ChromeProfile"
```

#### macOS
```bash
# 创建配置目录
mkdir -p ~/selenium/ChromeProfile

# 启动 Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/selenium/ChromeProfile"
```

### 开发环境使用

```bash
# 运行价格审核
npm run price

# 运行合规审核
npm run compliance

# 运行所有功能
npm run dev
```

## 命令行参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--price` | 仅运行价格审核 | `temu-auto --price` |
| `--compliance` | 仅运行合规审核 | `temu-auto --compliance` |
| `--port=<端口号>` | 指定浏览器调试端口 | `temu-auto --port=9223` |
| `--help` 或 `-h` | 显示帮助信息 | `temu-auto --help` |
| `--version` 或 `-v` | 显示版本信息 | `temu-auto --version` |

## 开发指南

### 项目结构

```
temu-seller-automation/
├── src/                # 源代码目录
│   ├── core/          # 核心功能
│   ├── services/      # 业务服务
│   └── utils/         # 工具函数
├── dist/              # 编译输出目录
├── tests/             # 测试文件
└── package.json       # 项目配置
```

### 开发命令

```bash
# 运行开发环境
npm run dev

# 运行测试
npm test

# 代码检查
npm run lint

# 编译项目
npm run build
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

ISC 

## 运行
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/selenium/ChromeProfile"

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"

为什么你通过"div.rocket-select-item-option-content >> text='100 条/页'",这种写法就能找到对应的选项，而且选对了，我都没告诉你对应的选择器

让我解释一下这个选择器的工作原理：
div.rocket-select-item-option-content 是基础选择器，它选择具有 rocket-select-item-option-content 类的 div 元素。这个类名是 Rocket UI 组件库（一个类似 Ant Design 的组件库）中下拉选项的标准类名。
>> text='100 条/页' 是 Playwright 特有的文本选择器语法，它会：
查找包含精确文本 "100 条/页" 的元素
这个文本选择器会自动处理文本节点的匹配，不管文本是在元素内部还是作为子元素
为什么我知道这个选择器：
从你之前提供的 HTML 结构中，我看到了下拉选项的基本结构
在 Rocket UI 这样的组件库中，下拉选项通常使用固定的类名和结构
rocket-select-item-option-content 是这类组件库中常用的选项内容类名
举个例子，下拉选项的 HTML 结构可能是这样的：
Apply to README.md
>
或者这样的：
Apply to README.md
>
Playwright 的 >> text= 选择器都能正确处理这两种情况，这就是为什么它能准确找到并选择正确的选项。
这种选择器的优点是：
更可靠：不依赖于具体的 DOM 结构
更灵活：可以处理文本在不同层级的情况
更易读：直接使用可见文本进行选择
这就是为什么这个选择器能准确找到并选择正确的选项，即使你没有提供具体的选择器。