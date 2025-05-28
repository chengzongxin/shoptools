@echo off
REM 用 PowerShell 调用 Python 脚本，支持中文路径
powershell -NoProfile -ExecutionPolicy Bypass -Command "python 'C:\Users\Administrator\Desktop\shoptools\生成商品码\product_list_crawler.py'"
pause