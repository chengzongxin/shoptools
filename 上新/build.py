import PyInstaller.__main__
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定义资源文件路径
chromedriver_path = os.path.join(current_dir, "drivers", "chromedriver.exe")
chromedriver_win64_path = os.path.join(current_dir, "drivers", "chromedriver-win64")

# 定义打包参数
params = [
    'main.py',  # 主程序文件
    '--name=网页自动化工具',  # 可执行文件名称
    '--onefile',  # 打包成单个文件
    '--noconfirm',  # 不询问确认
    f'--add-data={chromedriver_path};drivers',  # 添加chromedriver
    f'--add-data={chromedriver_win64_path};drivers/chromedriver-win64',  # 添加chromedriver-win64目录
    '--clean',  # 清理临时文件
]

# 执行打包命令
PyInstaller.__main__.run(params) 