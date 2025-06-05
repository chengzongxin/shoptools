# Temu卖家自动化工具

这是一个基于 Playwright + TypeScript 开发的 Temu 卖家自动化工具，用于简化日常上新工作流程。

## 项目结构

```
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   ├── services/          # 业务服务层
│   ├── utils/             # 工具函数
│   └── index.ts           # 入口文件
├── tests/                 # 测试文件目录
├── logs/                  # 日志文件目录
├── package.json           # 项目配置文件
├── tsconfig.json          # TypeScript 配置
└── playwright.config.ts   # Playwright 配置
```

## 功能特性

- 自动化登录
- 商品上新
- 库存管理
- 订单处理
- 数据统计

## 开发环境要求

- Node.js >= 16
- npm >= 7

## 安装

```bash
# 安装依赖
npm install

# 安装 Playwright 浏览器
npx playwright install
```

## 使用说明

1. 开发模式运行：
```bash
npm run dev
```

2. 构建项目：
```bash
npm run build
```

3. 运行测试：
```bash
npm test
```

## 配置说明

1. 在项目根目录创建 `.env` 文件
2. 配置必要的环境变量：
   - TEMU_USERNAME: Temu 卖家账号
   - TEMU_PASSWORD: Temu 卖家密码

## 注意事项

- 请确保网络环境稳定
- 建议使用代理服务器访问 Temu 卖家后台
- 定期检查并更新依赖包版本

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

ISC 

## 运行
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/selenium/ChromeProfile"



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