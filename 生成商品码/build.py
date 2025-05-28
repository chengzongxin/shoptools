import os
import subprocess
import sys

def build_exe():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 确保在正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 安装依赖
    print("安装依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 使用PyInstaller打包
    print("使用PyInstaller打包...")
    subprocess.check_call([
        "pyinstaller",
        "--name=商品数据爬取工具",
        "--windowed",  # 不显示控制台窗口
        "--add-data=README.md;.",  # 添加README文件
        "--clean",  # 清理临时文件
        "product_list_crawler.py"
    ])
    
    print("构建完成！")
    print("可执行文件位于 dist/商品数据爬取工具/商品数据爬取工具.exe")

if __name__ == "__main__":
    build_exe() 