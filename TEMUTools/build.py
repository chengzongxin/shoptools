import os
import shutil
import subprocess
import sys

def clean_build_dirs():
    """清理构建目录"""
    print("正在清理构建目录...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除 {dir_name} 目录")

def build_app(dev_mode=False):
    """构建应用程序
    
    Args:
        dev_mode (bool): 是否为开发模式（包含控制台窗口）
    """
    print("开始构建应用程序...")
    
    # 基础命令
    cmd = [
        'pyinstaller',
        '--name="TEMU工具集"',
        'src/main.py'
    ]
    
    # 根据模式添加参数
    if dev_mode:
        cmd.insert(1, '--windowed')
        print("开发模式：包含控制台窗口")
    else:
        cmd.insert(1, '--noconsole')
        print("生产模式：不包含控制台窗口")
    
    # 执行打包命令
    try:
        subprocess.run(' '.join(cmd), shell=True, check=True)
        print("打包完成！")
        print(f"可执行文件位置: {os.path.abspath('dist/TEMU工具集')}")
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    # 检查命令行参数
    dev_mode = '--dev' in sys.argv
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 构建应用
    build_app(dev_mode)

if __name__ == "__main__":
    main() 