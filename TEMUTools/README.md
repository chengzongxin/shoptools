# TEMU工具集

一个用于TEMU卖家的工具集合，帮助自动化商品管理流程。

## 功能特点

- 商品列表管理
   - 商品码模板生成
- 库存模板管理
- 自动保存配置
- 数据导出功能

## 环境要求

- Python 3.8 或更高版本
- Windows 操作系统

## 安装步骤

1. 克隆或下载项目代码

2. 创建并激活虚拟环境（推荐）：
   ```bash
   # 创建虚拟环境
   python setup_venv.py
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
   ```bash
   python src/main.py
   ```

2. 在商品列表管理标签页中：
   - 输入Cookie、Anti-content和MallID
   - 设置获取页数和每页数据量
   - 点击"开始爬取"按钮
   - 数据获取完成后可以点击"导出数据"按钮导出为CSV文件

3. 配置会自动保存，下次启动时会自动加载上次的配置

## 打包说明

使用以下命令打包程序：

```bash
# 开发模式（包含控制台窗口）
python build.py --dev

# 生产模式（不包含控制台窗口）
python build.py
```

打包后的程序将在 `dist/TEMU工具集` 目录中。

## 注意事项

1. 请确保已正确安装Python环境
2. 建议使用虚拟环境运行程序
3. 首次运行需要配置Cookie等信息
4. 导出的CSV文件可以直接用Excel打开

## 常见问题

1. 如果遇到权限问题，请以管理员身份运行
2. 如果程序无法启动，请检查Python环境是否正确
3. 如果数据获取失败，请检查Cookie等信息是否正确

## 开发说明

- 项目使用模块化设计
- 每个功能模块独立开发
- 使用tkinter构建GUI界面
- 配置文件保存在项目根目录

## 许可证

MIT License


合并流程：
选择违规列表Excel文件
选择商品列表Excel文件
选择保存目录
进行数据合并
保存合并后的文件


   # 🐍 macOS 下 Python tkinter 无法使用问题总结

   ## 🧩 问题现象

   在使用 `pyenv` 安装 Python 3.11.9 后，尝试导入 `tkinter` 模块时报错：

   ```bash
   ModuleNotFoundError: No module named '_tkinter'
   ```

   并且使用 `python3 -m tkinter` 测试失败。

   ---

   ## 🎯 问题原因

   macOS 使用 Homebrew 安装的 `tcl-tk` 默认是 **9.0 预发布版**，而 Python 3.11.x 的官方编译器尚不支持 `tcl-tk 9.0`，因此：

   - pyenv 编译 Python 时无法正确链接到 `libtk` 和 `libtcl`；
   - 导致最终生成的 `_tkinter` 模块缺失。

   ---

   ## 🛠 解决方案

   1. **卸载 tcl-tk 9.0**（会与 tkinter 不兼容）：

      ```bash
      brew uninstall --ignore-dependencies tcl-tk
      ```

   2. **安装兼容的 tcl-tk@8 版本**：

      ```bash
      brew install tcl-tk@8
      ```

   3. **设置环境变量，让 pyenv 编译时链接正确版本的 Tcl/Tk**：

      ```bash
      export PATH="/opt/homebrew/opt/tcl-tk@8/bin:$PATH"
      export LDFLAGS="-L/opt/homebrew/opt/tcl-tk@8/lib"
      export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk@8/include"
      export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk@8/lib/pkgconfig"
      ```

   4. **重新编译安装 Python，并显式指定 Tcl/Tk 的路径**：

      ```bash
      env PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I/opt/homebrew/opt/tcl-tk@8/include' --with-tcltk-libs='-L/opt/homebrew/opt/tcl-tk@8/lib'" \
         pyenv install 3.11.9
      ```

   5. **设为默认版本**：

      ```bash
      pyenv global 3.11.9
      ```

   6. **验证 tkinter 是否成功**：

      ```bash
      python3 -m tkinter
      ```

      成功后会弹出一个 `tk` 小窗口，证明 tkinter 可用 ✅。

   ---

   ## ✅ 补充建议

   如果你频繁使用 pyenv 安装 Python，建议将 `tcl-tk@8` 永久加入 shell 的配置文件，例如 `.zshrc`：

   ```bash
   export PATH="/opt/homebrew/opt/tcl-tk@8/bin:$PATH"
   export LDFLAGS="-L/opt/homebrew/opt/tcl-tk@8/lib"
   export CPPFLAGS="-I/opt/homebrew/opt/tcl-tk@8/include"
   export PKG_CONFIG_PATH="/opt/homebrew/opt/tcl-tk@8/lib/pkgconfig"
   ```