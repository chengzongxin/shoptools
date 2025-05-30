import os
import shutil
import subprocess
import sys
import time

def clean_build_dirs():
    """清理构建目录"""
    print("正在清理构建目录...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"已删除 {dir_name} 目录")
            except PermissionError as e:
                print(f"警告：无法删除 {dir_name} 目录中的某些文件，可能是文件正在使用中")
                print(f"错误信息：{str(e)}")
                print("请关闭所有相关程序后重试")
                sys.exit(1)
            except Exception as e:
                print(f"删除 {dir_name} 目录时出错：{str(e)}")
                sys.exit(1)

def build_app(dev_mode=False):
    """构建应用程序
    
    Args:
        dev_mode (bool): 是否为开发模式（包含控制台窗口）
    """
    print("开始构建应用程序...")
    
    # 检查图标文件是否存在
    icon_path = os.path.join('assets', 'app.ico')
    if not os.path.exists(icon_path):
        print(f"警告：图标文件 {icon_path} 不存在，将使用默认图标")
        icon_option = []
    else:
        icon_option = ['--icon', icon_path]
    
    # 基础命令
    cmd = [
        'pyinstaller',
        '--name=TEMU工具集',  # 移除多余的引号
        'src/main.py'
    ]
    
    # 添加图标选项
    if icon_option:
        cmd[1:1] = icon_option
    
    # 根据模式添加参数
    if dev_mode:
        cmd.insert(1, '--windowed')
        print("开发模式：包含控制台窗口")
    else:
        cmd.insert(1, '--noconsole')
        print("生产模式：不包含控制台窗口")
    
    # 执行打包命令
    try:
        print("执行命令:", ' '.join(cmd))
        subprocess.run(cmd, check=True)  # 移除shell=True，直接传递命令列表
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