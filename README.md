# TEMU工具集

## 项目简介
TEMU工具集是一个专门为TEMU卖家设计的自动化工具集合，旨在简化卖家上新流程，提高工作效率。该工具集采用模块化设计，每个功能模块独立运行，互不影响。

## 功能模块
1. 商品列表管理
   - 商品列表爬取
   - 商品码模板生成
   - 库存模板生成

## 开发环境要求
- Python 3.8+
- Windows 10/11

## 依赖包安装
```bash
pip install -r requirements.txt
```

## 项目结构
```
TEMU工具集/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── modules/
│       ├── __init__.py
│       └── product_list/
│           ├── __init__.py
│           ├── crawler.py
│           └── gui.py
├── data/
│   └── .gitkeep
└── dist/
    └── .gitkeep
```

## 打包命令
使用PyInstaller打包应用程序：

```bash
# 开发环境打包（包含控制台窗口）
pyinstaller --name="TEMU工具集" --windowed --icon=src/assets/icon.ico --add-data="src/assets;assets" src/main.py

# 生产环境打包（不包含控制台窗口）
pyinstaller --name="TEMU工具集" --noconsole --icon=src/assets/icon.ico --add-data="src/assets;assets" src/main.py
```

打包后的文件将生成在`dist/TEMU工具集`目录下。

## 使用说明
1. 运行打包后的`TEMU工具集.exe`
2. 在界面中选择需要使用的功能模块
3. 按照界面提示进行操作

## 注意事项
1. 首次运行前请确保已安装所有依赖包
2. 使用商品列表爬取功能时，需要从浏览器开发者工具中获取Cookie、Anti-content和MallID
3. 生成的文件将保存在`data`目录下

## 开发计划
- [x] 商品列表爬取功能
- [ ] 商品码模板生成功能
- [ ] 库存模板生成功能
- [ ] 其他功能模块开发中...

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证
MIT License 