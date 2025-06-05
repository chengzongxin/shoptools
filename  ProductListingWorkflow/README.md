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