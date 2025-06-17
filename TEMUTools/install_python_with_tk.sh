#!/bin/bash

set -e

echo "🔧 开始修复 tkinter 缺失问题..."

# 1. 强制卸载 tcl-tk 9.0.1（它和 tkinter 不兼容）
echo "🧹 正在卸载 tcl-tk@9.0.1..."
brew uninstall --ignore-dependencies tcl-tk || true

# 2. 安装 tcl-tk@8
echo "⬇️ 正在安装 tcl-tk@8..."
brew install tcl-tk@8

# 3. 设置环境变量（当前终端生效）
echo "🔧 设置环境变量..."
export PATH="/opt/homebrew/opt/tcl-tk@8/bin:$PATH"
export LDFLAGS="-L/opt/homebrew/opt/tcl-tk@8/lib"
export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk@8/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk@8/lib/pkgconfig"

# 4. 删除原来的 Python 3.11.9 安装（如果有）
echo "🧹 删除已有的 Python 3.11.9（如果有）..."
pyenv uninstall -f 3.11.9 || true

# 5. 使用 pyenv 安装 Python 3.11.9 并启用 tcl-tk
echo "⬇️ 使用 pyenv 安装 Python 3.11.9（带 tkinter）..."
env PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/opt/homebrew/opt/tcl-tk@8/include' --with-tcltk-libs='-L/opt/homebrew/opt/tcl-tk@8/lib'" \
    pyenv install 3.11.9

# 6. 设置默认版本
echo "✅ 设置 3.11.9 为全局默认 Python 版本..."
pyenv global 3.11.9

# 7. 测试 tkinter 是否可用
echo "🧪 测试 tkinter 是否安装成功..."
python3 -m tkinter || {
  echo "❌ tkinter 测试失败，请检查编译日志"
  exit 1
}

echo "✅ Python 3.11.9 安装完成，tkinter 可用！"
