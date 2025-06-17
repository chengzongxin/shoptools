import os
import sys
import shutil
import subprocess

def build_executable():
    """打包可执行文件"""
    print("开始打包...")
    
    # 确保 PyInstaller 已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 清理旧的构建文件
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("TEMUTools.spec"):
        os.remove("TEMUTools.spec")
    
    # 创建打包命令
    sep = ';' if sys.platform.startswith('win') else ':'
    cmd = [
        "pyinstaller",
        "--name=TEMUTools",
        "--windowed",  # 不显示控制台窗口
        "--icon=assets/icon.ico",  # 应用图标
        f"--add-data=assets{sep}assets",  # 添加资源文件
        "--hidden-import=PIL._tkinter_finder",  # 添加隐藏导入
        "--noconfirm",  # 不询问确认
        "--clean",  # 清理临时文件
        "src/main.py"  # 主程序入口
    ]
    
    # 执行打包命令
    print("正在执行打包命令...")
    subprocess.check_call(cmd)
    
    # 复制配置文件到打包目录
    print("正在复制配置文件...")
    if os.path.exists("config.json"):
        shutil.copy("config.json", "dist/TEMUTools/")
    
    print("打包完成！")
    print("可执行文件位于: dist/TEMUTools/TEMUTools.exe")

if __name__ == "__main__":
    build_executable() 