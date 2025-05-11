# 链接重复检测工具

这是一个用于检测文件夹中重复链接的工具。

## 功能特点

- 支持检测文件夹中的重复链接
- 可以识别跨文件的重复链接
- 可以识别单个文件中的重复链接
- 支持删除重复链接
- 提供清空功能

## 使用说明

1. 点击"选择文件夹"按钮选择要检测的文件夹
2. 等待检测完成
3. 查看检测结果
4. 如需删除重复链接，点击"删除重复链接"按钮
5. 如需重新开始，点击"清空"按钮

## 系统要求

- Windows 10 或更高版本
- macOS 10.13 或更高版本

## 注意事项

- 请确保有足够的权限访问和修改目标文件夹
- 建议在删除重复链接前备份重要文件 

## win打包命令
pyinstaller --windowed --name "链接检测工具" link_checker.py

## mac打包命令
pip3 install pyinstaller
pyinstaller --windowed --name "链接检测工具" link_checker.py

sudo pyinstaller --windowed --name "链接检测工具" link_checker.py