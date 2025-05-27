import PyInstaller.__main__
import os
import platform

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 根据操作系统设置路径分隔符和文件名
system = platform.system()
if system == "Windows":
    separator = ";"
    driver_name = "chromedriver.exe"
    driver_dir = "chromedriver-win64"
    exe_name = "网页自动化工具.exe"
else:
    separator = ":"
    driver_name = "chromedriver"
    driver_dir = "chromedriver-mac-x64"
    exe_name = "网页自动化工具"

# 定义资源文件路径
chromedriver_path = os.path.join(current_dir, "drivers", driver_name)
chromedriver_dir_path = os.path.join(current_dir, "drivers", driver_dir)

# 定义打包参数
params = [
    'main.py',  # 主程序文件
    f'--name={exe_name}',  # 可执行文件名称
    '--onefile',  # 打包成单个文件
    '--noconfirm',  # 不询问确认
    f'--add-data={chromedriver_path}{separator}drivers',  # 添加chromedriver
    f'--add-data={chromedriver_dir_path}{separator}drivers/{driver_dir}',  # 添加chromedriver目录
    '--clean',  # 清理临时文件
]

# 执行打包命令
PyInstaller.__main__.run(params) 