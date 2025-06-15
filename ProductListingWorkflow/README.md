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

## Windows 使用指南

### 1. 安装工具

```bash
# 以管理员身份运行 PowerShell 或命令提示符
# 安装工具
npm install -g temu-seller-automation
```
##### 如果PowerShell运行报错
问题分析
我看到你在 PowerShell 中运行 npm -v 命令时遇到了权限错误。这个错误提示说系统禁止运行脚本，这是一个 PowerShell 的执行策略（Execution Policy）限制导致的问题。
错误原因解释
PowerShell 默认的安全策略比较严格，默认情况下不允许运行脚本
错误信息中的 "about_Execution_Policies" 链接指向了微软的官方文档，说明了这个限制
而 CMD 没有这样的限制，所以可以在 CMD 中正常运行
解决方案
我建议通过以下步骤解决这个问题：
首先，让我们以管理员身份运行 PowerShell 并修改执行策略。我会帮你执行这个命令

```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 启动 Chrome 浏览器

在 Windows 上，需要先启动 Chrome 浏览器：

```bash
# 创建配置目录（在 C 盘根目录下）
mkdir C:\selenium\ChromeProfile
# & 是 PowerShell 中的调用运算符，用来运行带空格路径的可执行文件。
# 如果不加 &，PowerShell 会把整个字符串看成一个普通字符串，而不是命令。
# 启动 Chrome（使用完整路径）
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\ChromeProfile"

```

注意：
- 如果 Chrome 安装在其他位置，需要修改路径
- 确保路径中没有空格，如果有空格需要用引号括起来
- 建议创建一个批处理文件（.bat）来简化启动过程

### 3. 创建启动脚本

创建一个 `start-chrome.bat` 文件：

```batch
@echo off
echo 正在启动 Chrome 浏览器...
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenium\ChromeProfile"
```

### 4. 使用工具

```bash
# 运行所有功能
temu-auto

# 只运行价格审核
temu-auto --price

# 只运行合规审核
temu-auto --compliance

# 使用不同的端口（如果默认端口被占用）
temu-auto --port=9223

# 查看帮助信息
temu-auto --help
```

### 5. 常见问题解决

1. **如果命令不可用**
```bash
# 检查是否安装成功
npm list -g temu-seller-automation

# 检查环境变量
echo %PATH%

# 重新安装
npm uninstall -g temu-seller-automation
npm install -g temu-seller-automation
```

2. **如果 Chrome 路径不对**
- 找到 Chrome 的实际安装位置
- 修改启动脚本中的路径
- 常见的安装位置：
  ```
  C:\Program Files\Google\Chrome\Application\chrome.exe
  C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
  ```

3. **如果端口被占用**
```bash
# 使用不同的端口
temu-auto --port=9223
```

### 6. 创建快捷方式

1. **创建桌面快捷方式**
   - 右键桌面 -> 新建 -> 快捷方式
   - 输入命令：`cmd /k "temu-auto --price"`
   - 设置名称：`Temu价格审核`

2. **创建批处理文件**
```batch
@echo off
echo 正在启动 Temu 自动化工具...
temu-auto --price
pause
```

### 7. 使用建议

1. **首次使用**
   - 先运行 `temu-auto --help` 查看帮助信息
   - 确保 Chrome 浏览器已经正确启动
   - 建议先运行单个功能进行测试

2. **日常使用**
   - 先运行 Chrome 浏览器
   - 然后运行自动化工具
   - 可以根据需要选择运行特定功能

3. **注意事项**
   - 确保网络连接稳定
   - 确保 Chrome 浏览器版本兼容
   - 建议定期更新工具版本

### 8. 完整使用流程

1. **启动 Chrome**
   - 运行 `start-chrome.bat`
   - 等待浏览器完全启动

2. **运行工具**
   - 打开新的命令提示符
   - 运行 `temu-auto --price` 或 `temu-auto --compliance`

3. **查看结果**
   - 观察命令行的输出信息
   - 检查浏览器中的操作结果

## macOS 使用指南

### 1. 安装工具

```bash
# 使用 sudo 安装
sudo npm install -g temu-seller-automation
```

### 2. 启动 Chrome 浏览器

```bash
# 创建配置目录
mkdir -p ~/selenium/ChromeProfile

# 启动 Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/selenium/ChromeProfile"
```

### 3. 使用工具

```bash
# 运行价格审核
temu-auto --price

# 运行合规审核
temu-auto --compliance
```

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


## 全局cli
bin:
"temu-auto": "./dist/cli.js"

scripts
"build": "tsc && node scripts/prepare-cli.js",

# 更新版本号
npm version patch

# 发布
npm publish

# 卸载旧版本
sudo npm uninstall -g temu-seller-automation

# 安装新版本
sudo npm install -g temu-seller-automation

# 检查安装
npm list -g temu-seller-automation

# 运行命令
temu-auto --help