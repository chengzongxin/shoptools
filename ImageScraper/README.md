 # ImageScraper 打包说明

## Windows 系统打包命令
```bash
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico --name="ImageScraper" gui.py
```

## Mac 系统打包命令
```bash
# 首先确保已安装 PyInstaller
pip install pyinstaller

# 打包命令
pyinstaller --noconfirm --onefile --windowed --icon=icon.icns --name="ImageScraper" gui.py
```

## 打包说明
1. Windows 系统使用 `.ico` 格式的图标文件
2. Mac 系统使用 `.icns` 格式的图标文件
3. 打包后的可执行文件将在 `dist` 目录下生成
4. Windows 系统生成 `.exe` 文件
5. Mac 系统生成无扩展名的可执行文件

## 注意事项
1. 确保已安装所有依赖包
2. 确保图标文件存在于项目目录中
3. Mac 系统可能需要授予执行权限：`chmod +x dist/ImageScraper`