import os
import subprocess
import sys
import venv
from pathlib import Path

def create_venv():
    """创建虚拟环境"""
    print("正在创建虚拟环境...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    venv_path = project_root / "venv"
    
    # 检查虚拟环境是否已存在
    if venv_path.exists():
        print("虚拟环境已存在，是否重新创建？(y/n)")
        if input().lower() != 'y':
            print("取消创建虚拟环境")
            return
        # 删除旧的虚拟环境
        import shutil
        shutil.rmtree(venv_path)
    
    # 创建虚拟环境
    venv.create(venv_path, with_pip=True)
    print(f"虚拟环境已创建在: {venv_path}")
    
    # 获取虚拟环境中的 Python 解释器路径
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        python_path = venv_path / "bin" / "python"
        pip_path = venv_path / "bin" / "pip"
    
    # 升级 pip
    print("正在升级 pip...")
    subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    
    # 安装依赖
    print("正在安装依赖...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
    
    print("\n虚拟环境设置完成！")
    print("\n使用方法：")
    print("1. 激活虚拟环境：")
    if sys.platform == "win32":
        print(f"   {venv_path}\\Scripts\\activate")
    else:
        print(f"   source {venv_path}/bin/activate")
    print("\n2. 运行程序：")
    print("   python src/main.py")
    print("\n3. 退出虚拟环境：")
    print("   deactivate")

if __name__ == "__main__":
    create_venv() 