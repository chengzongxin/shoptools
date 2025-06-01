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


{
  "cookie": "api_uid=Ctxz/mgXjlV6CABNVNWbAg==; _bee=jOHrLzfH6NtGxvbUWZF2S2QS8p5wSapE; njrpl=jOHrLzfH6NtGxvbUWZF2S2QS8p5wSapE; dilx=rHHJULtHYX0y-syqPWiDr; hfsc=L3yOfo0y4Tz80J7Feg==; timezone=Asia%2FShanghai; _nano_fp=XpmYl0mjnq98X0dyno_fxwbYByrCp0Y6TCwjmMZT; seller_temp=N_eyJ0Ijoidko5M1lQSHppSnRSdmtlbW5Bb2gzN01NeFBaTldLQnVuU1Z0M3lBWFlFUWxKZWpUQnhaWjhnMlRBZnNDSGhZZ2RWRHo1Q3k0bTl1OTQrT3RRczAvd1E9PSIsInYiOjEsInMiOjEwMDAxLCJ1IjoyNDE1MTU0NjgxNzcwMX0=; mallid=634418223796259",
  "anti_content": "0aqAfxiUGslaU99VUcmM0whphwBXntrmM2cfwZCCqTPPEs9X_DU4CmiklittuPqUDCbX1Zb-5039HL2hqSZlb5B8WYDSSJWNVRFs47jklpmt9Izvx0_twQwUMUA4izPR_cjf6ybFTNOs62XFLb5kpVzrISJY37cLALbMO35MguEjyjO-9C5FnQyCIgpMwTayHp8c-t7y8ue-o2UKm_qtpWmNqCOICVURFqX37KfzF8CPwzvatgCVwtP__gGIU6COp3YB5q4wkqH-P2XKi3cJFb45NNehBB5hma4qa8FYL4Bpw7i26pKVPDNpiF-rX9WAXZWZEv18BZm40-mxBcMdgc4ty90yH7zXri3jJJL7EIZDT5d7cZ2QDQnPA-bUVc0GK-l5Gap3LoHWHf0SJrFdqbC7d7hCWgw5DCdHRuzsBRCQrvM7KiEjvIHjRKrjz-3S6DqMMI386iiW4HWhQwSpD1ETKbS",
  "mallid": "634418223796259"
}