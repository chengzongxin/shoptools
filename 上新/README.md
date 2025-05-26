# 网页自动化工具

这是一个基于 Selenium 的网页自动化项目，用于模拟用户操作。

## 环境要求
- Python 3.8+
- Chrome 浏览器
- Windows 操作系统

## 安装步骤

1. 安装依赖包：
```bash
pip install -r requirements.txt
```

2. 配置 Chrome 浏览器：
   - 确保已安装 Chrome 浏览器
   - 创建目录：`C:\selenum\ChromeProfile`
   - 运行 `start_chrome.bat` 启动调试模式的 Chrome

## 运行方式

### 方式一：直接运行 Python 脚本
```bash
python main.py
```

### 方式二：运行打包后的可执行文件
1. 进入 `dist` 目录
2. 运行 `网页自动化工具.exe`

## 打包说明

如果需要重新打包程序，请按以下步骤操作：

1. 确保已安装 PyInstaller：
```bash
pip install pyinstaller
```

2. 运行打包脚本：
```bash
python build.py
```

3. 打包完成后，可执行文件将生成在 `dist` 目录下

## 注意事项

1. 运行程序前，请确保：
   - Chrome 浏览器已安装
   - 已运行 `start_chrome.bat` 启动调试模式的 Chrome
   - `C:\selenum\ChromeProfile` 目录存在

2. 如果程序无法启动：
   - 检查 Chrome 浏览器是否正常运行
   - 查看控制台输出的错误信息
   - 确保所有依赖文件都在正确的位置

3. 常见问题解决：
   - 如果提示找不到 ChromeDriver，请检查 `drivers` 目录是否存在
   - 如果浏览器无法启动，请检查 Chrome 安装路径是否正确
   - 如果出现权限问题，请以管理员身份运行程序

## 项目结构
- `main.py`: 主程序文件
- `config.py`: 配置文件
- `requirements.txt`: 项目依赖文件
- `drivers/`: ChromeDriver 相关文件
- `modules/`: 功能模块目录
- `logs/`: 日志文件目录

## 调试模式

在 `config.py` 中可以设置 `DEBUG = True` 来启用调试模式，这将显示更详细的运行信息。

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"

python main.py