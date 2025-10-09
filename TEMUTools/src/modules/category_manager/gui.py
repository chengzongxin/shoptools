"""
品类配置管理GUI模块
提供品类的增删改查、启用/禁用、图片管理等功能
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from typing import Optional, Dict
from ..config.config import category_config


class CategoryManagerTab(ttk.Frame):
    """品类配置管理标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        """设置用户界面"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(
            title_frame, 
            text="商品类别配置管理", 
            font=('Arial', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            title_frame, 
            text="📖 使用说明", 
            command=self.show_help
        ).pack(side=tk.RIGHT, padx=5)
        
        # 工具栏
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(
            toolbar_frame, 
            text="➕ 新增品类", 
            command=self.add_category
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar_frame, 
            text="✏️ 编辑品类", 
            command=self.edit_category
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar_frame, 
            text="🗑️ 删除品类", 
            command=self.delete_category
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(
            toolbar_frame, 
            text="✅ 启用选中", 
            command=lambda: self.toggle_enabled(True)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar_frame, 
            text="❌ 禁用选中", 
            command=lambda: self.toggle_enabled(False)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(
            toolbar_frame, 
            text="🔄 刷新列表", 
            command=self.load_categories
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar_frame, 
            text="📁 打开图片目录", 
            command=self.open_images_folder
        ).pack(side=tk.LEFT, padx=5)
        
        # 列表区域
        list_frame = ttk.LabelFrame(main_frame, text="品类列表", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 创建Treeview
        columns = ('name', 'cate_id', 'image_file', 'price_threshold', 'code_mapping', 'enabled')
        self.tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show='headings', 
            height=15,
            selectmode='extended'
        )
        
        # 设置列标题和宽度
        self.tree.heading('name', text='品类名称')
        self.tree.heading('cate_id', text='类别ID')
        self.tree.heading('image_file', text='实拍图文件')
        self.tree.heading('price_threshold', text='价格底线(元)')
        self.tree.heading('code_mapping', text='商品码')
        self.tree.heading('enabled', text='状态')
        
        self.tree.column('name', width=150)
        self.tree.column('cate_id', width=80)
        self.tree.column('image_file', width=200)
        self.tree.column('price_threshold', width=100)
        self.tree.column('code_mapping', width=100)
        self.tree.column('enabled', width=60)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 双击编辑
        self.tree.bind('<Double-Button-1>', lambda e: self.edit_category())
        
        # 统计信息区域
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.info_label = ttk.Label(info_frame, text="", foreground='gray')
        self.info_label.pack(side=tk.LEFT)
        
        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def load_categories(self):
        """加载品类列表"""
        # 清空现有项
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 刷新配置并加载
        category_config.refresh_cache()
        categories = category_config.get_categories()
        
        enabled_count = 0
        disabled_count = 0
        
        for category in categories:
            category_id = category.get('id', '')  # 内部唯一ID
            name = category.get('name', '')
            cate_id = category.get('cate_id', 0)
            image_file = category.get('image_file', '')
            price_threshold = category.get('price_threshold', 0.0)
            code_mapping = category.get('code_mapping', '')
            enabled = category.get('enabled', True)
            
            if enabled:
                enabled_count += 1
                status = '✅ 启用'
                tags = ('enabled',)
            else:
                disabled_count += 1
                status = '❌ 禁用'
                tags = ('disabled',)
            
            # 使用iid参数存储内部ID，这样可以通过iid直接获取
            self.tree.insert(
                '', 
                tk.END,
                iid=str(category_id),  # 使用内部ID作为item的标识符
                values=(name, cate_id, image_file, price_threshold, code_mapping, status),
                tags=tags
            )
        
        # 配置标签样式
        self.tree.tag_configure('enabled', foreground='black')
        self.tree.tag_configure('disabled', foreground='gray')
        
        # 更新统计信息
        total = len(categories)
        self.info_label.config(
            text=f"总计: {total} 个品类  |  启用: {enabled_count}  |  禁用: {disabled_count}"
        )
    
    def add_category(self):
        """新增品类"""
        dialog = CategoryEditDialog(self, title="新增品类")
        if dialog.result:
            category_data = dialog.result
            if category_config.add_category(category_data):
                messagebox.showinfo("成功", "品类添加成功！")
                self.load_categories()
            else:
                messagebox.showerror("错误", "品类添加失败！")
    
    def edit_category(self):
        """编辑品类"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要编辑的品类！")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("提示", "一次只能编辑一个品类！")
            return
        
        item = selection[0]
        
        # 获取完整的品类数据（使用内部唯一ID）
        category_id = int(item)  # iid就是内部ID
        category_data = category_config.get_category_by_id(category_id)
        
        if not category_data:
            messagebox.showerror("错误", "无法获取品类信息！")
            return
        
        dialog = CategoryEditDialog(self, title="编辑品类", category_data=category_data)
        if dialog.result:
            updated_data = dialog.result
            if category_config.update_category(category_id, updated_data):
                messagebox.showinfo("成功", "品类更新成功！")
                self.load_categories()
            else:
                messagebox.showerror("错误", "品类更新失败！")
    
    def delete_category(self):
        """删除品类"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的品类！")
            return
        
        count = len(selection)
        if not messagebox.askyesno("确认", f"确定要删除选中的 {count} 个品类吗？\n\n注意：此操作不可恢复！"):
            return
        
        success_count = 0
        for item in selection:
            category_id = int(item)  # 使用内部唯一ID
            if category_config.delete_category(category_id):
                success_count += 1
        
        messagebox.showinfo("完成", f"成功删除 {success_count}/{count} 个品类")
        self.load_categories()
    
    def toggle_enabled(self, enabled: bool):
        """切换品类启用状态"""
        selection = self.tree.selection()
        if not selection:
            action = "启用" if enabled else "禁用"
            messagebox.showwarning("提示", f"请先选择要{action}的品类！")
            return
        
        success_count = 0
        for item in selection:
            category_id = int(item)  # 使用内部唯一ID
            if category_config.update_category(category_id, {"enabled": enabled}):
                success_count += 1
        
        action = "启用" if enabled else "禁用"
        messagebox.showinfo("完成", f"成功{action} {success_count}/{len(selection)} 个品类")
        self.load_categories()
    
    def open_images_folder(self):
        """打开图片目录"""
        images_dir = category_config.get_images_dir()
        
        if not os.path.exists(images_dir):
            if messagebox.askyesno("提示", f"图片目录不存在：\n{images_dir}\n\n是否创建？"):
                try:
                    os.makedirs(images_dir, exist_ok=True)
                    messagebox.showinfo("成功", "图片目录创建成功！")
                except Exception as e:
                    messagebox.showerror("错误", f"创建目录失败：{str(e)}")
                    return
        
        # 根据操作系统打开文件夹
        import platform
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                os.system(f'open "{images_dir}"')
            elif system == "Windows":
                os.system(f'explorer "{images_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{images_dir}"')
        except Exception as e:
            messagebox.showerror("错误", f"打开目录失败：{str(e)}")
    
    def show_help(self):
        """显示使用说明"""
        help_text = """
品类配置管理使用说明

【主要功能】
1. 新增品类：点击"新增品类"按钮，填写品类信息
2. 编辑品类：选中品类后点击"编辑"，或双击品类行
3. 删除品类：选中品类后点击"删除"（支持多选）
4. 启用/禁用：选中品类后点击"启用选中"或"禁用选中"
5. 图片管理：点击"打开图片目录"，可直接管理实拍图文件

【字段说明】
• 品类名称：商品类别的中文名称
• 类别ID：TEMU系统中的类别ID（cate_id）
• 实拍图文件：对应的实拍图片文件名
• 价格底线：该类别商品的最低价格限制
• 商品码：用于生成商品编码的前缀映射

【注意事项】
1. 类别ID必须是唯一的
2. 图片文件必须存在于 assets/images 目录下
3. 禁用的品类不会在实拍图上传等功能中显示
4. 修改配置后会自动保存并刷新缓存

【快捷操作】
• 双击品类行：快速编辑
• Ctrl/Cmd+点击：多选品类
• Shift+点击：连续选择多个品类
        """
        
        help_window = tk.Toplevel(self)
        help_window.title("使用说明")
        help_window.geometry("600x500")
        
        text = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', help_text)
        text.config(state='disabled')
        
        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)


class CategoryEditDialog(tk.Toplevel):
    """品类编辑对话框"""
    
    def __init__(self, parent, title="编辑品类", category_data: Optional[Dict] = None):
        super().__init__(parent)
        self.title(title)
        self.geometry("600x500")
        self.resizable(False, False)
        
        self.result = None
        self.category_data = category_data or {}
        self.is_new = category_data is None
        
        self.setup_ui()
        self.center_window()
        
        # 模态对话框
        self.transient(parent)
        self.grab_set()
        self.wait_window()
    
    def setup_ui(self):
        """设置对话框界面"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 品类名称
        ttk.Label(main_frame, text="品类名称 *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value=self.category_data.get('name', ''))
        ttk.Entry(main_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 类别ID
        ttk.Label(main_frame, text="类别ID *").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cate_id_var = tk.StringVar(value=str(self.category_data.get('cate_id', '')))
        cate_id_entry = ttk.Entry(main_frame, textvariable=self.cate_id_var, width=40)
        cate_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        if not self.is_new:
            cate_id_entry.config(state='disabled')  # 编辑时不允许修改ID
        
        # 实拍图文件
        ttk.Label(main_frame, text="实拍图文件 *").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        image_frame = ttk.Frame(main_frame)
        image_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.image_file_var = tk.StringVar(value=self.category_data.get('image_file', ''))
        ttk.Entry(image_frame, textvariable=self.image_file_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(image_frame, text="选择文件", command=self.choose_image).pack(side=tk.LEFT, padx=(5, 0))
        
        # 价格底线
        ttk.Label(main_frame, text="价格底线(元) *").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.price_threshold_var = tk.StringVar(value=str(self.category_data.get('price_threshold', '0.0')))
        ttk.Entry(main_frame, textvariable=self.price_threshold_var, width=40).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 商品码
        ttk.Label(main_frame, text="商品码 *").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.code_mapping_var = tk.StringVar(value=self.category_data.get('code_mapping', ''))
        ttk.Entry(main_frame, textvariable=self.code_mapping_var, width=40).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 启用状态
        ttk.Label(main_frame, text="启用状态").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.enabled_var = tk.BooleanVar(value=self.category_data.get('enabled', True))
        ttk.Checkbutton(main_frame, text="启用该品类", variable=self.enabled_var).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 图片预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="图片预览", padding="5")
        preview_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.preview_label = ttk.Label(preview_frame, text="未选择图片", anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # 显示当前图片预览
        self.update_preview()
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="保存", command=self.save, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel, width=15).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def choose_image(self):
        """选择图片文件"""
        images_dir = category_config.get_images_dir()
        
        file_path = filedialog.askopenfilename(
            title="选择实拍图",
            initialdir=images_dir if os.path.exists(images_dir) else os.path.expanduser("~"),
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            # 规范化路径，解析符号链接和相对路径
            normalized_file_path = os.path.realpath(file_path)
            normalized_images_dir = os.path.realpath(images_dir)
            
            # 如果选择的文件不在图片目录中，询问是否复制
            if not normalized_file_path.startswith(normalized_images_dir):
                if messagebox.askyesno("提示", "选择的文件不在图片目录中，是否复制到图片目录？"):
                    try:
                        os.makedirs(images_dir, exist_ok=True)
                        filename = os.path.basename(file_path)
                        dest_path = os.path.join(images_dir, filename)
                        
                        # 如果目标文件已存在，询问是否覆盖
                        if os.path.exists(dest_path):
                            if not messagebox.askyesno("确认", f"文件 {filename} 已存在，是否覆盖？"):
                                return
                        
                        shutil.copy2(file_path, dest_path)
                        self.image_file_var.set(filename)
                        messagebox.showinfo("成功", "图片已复制到图片目录")
                        self.update_preview()
                    except Exception as e:
                        messagebox.showerror("错误", f"复制文件失败：{str(e)}")
                else:
                    return
            else:
                # 直接使用文件名
                filename = os.path.basename(file_path)
                self.image_file_var.set(filename)
                self.update_preview()
    
    def update_preview(self):
        """更新图片预览"""
        image_file = self.image_file_var.get()
        if not image_file:
            self.preview_label.config(text="未选择图片", image='')
            return
        
        images_dir = category_config.get_images_dir()
        image_path = os.path.join(images_dir, image_file)
        
        if not os.path.exists(image_path):
            self.preview_label.config(text=f"图片不存在：{image_file}", image='', foreground='red')
            return
        
        try:
            from PIL import Image, ImageTk
            
            # 加载图片并创建缩略图
            img = Image.open(image_path)
            img.thumbnail((400, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # 保持引用，防止被垃圾回收
            self.preview_label.photo = photo
            self.preview_label.config(image=photo, text='', foreground='black')
        except Exception as e:
            self.preview_label.config(text=f"图片加载失败：{str(e)}", image='', foreground='red')
    
    def save(self):
        """保存品类数据"""
        # 验证必填字段
        name = self.name_var.get().strip()
        cate_id_str = self.cate_id_var.get().strip()
        image_file = self.image_file_var.get().strip()
        price_threshold_str = self.price_threshold_var.get().strip()
        code_mapping = self.code_mapping_var.get().strip()
        
        if not name:
            messagebox.showwarning("提示", "请输入品类名称！")
            return
        
        if not cate_id_str:
            messagebox.showwarning("提示", "请输入类别ID！")
            return
        
        try:
            cate_id = int(cate_id_str)
        except ValueError:
            messagebox.showwarning("提示", "类别ID必须是数字！")
            return
        
        if not image_file:
            messagebox.showwarning("提示", "请选择实拍图文件！")
            return
        
        if not price_threshold_str:
            messagebox.showwarning("提示", "请输入价格底线！")
            return
        
        try:
            price_threshold = float(price_threshold_str)
        except ValueError:
            messagebox.showwarning("提示", "价格底线必须是数字！")
            return
        
        if not code_mapping:
            messagebox.showwarning("提示", "请输入商品码！")
            return
        
        # 验证图片文件是否存在
        images_dir = category_config.get_images_dir()
        image_path = os.path.join(images_dir, image_file)
        if not os.path.exists(image_path):
            if not messagebox.askyesno("警告", f"图片文件不存在：{image_file}\n\n是否仍要保存？"):
                return
        
        # 构建结果数据
        self.result = {
            'name': name,
            'cate_id': cate_id,
            'image_file': image_file,
            'price_threshold': price_threshold,
            'code_mapping': code_mapping,
            'enabled': self.enabled_var.get()
        }
        
        self.destroy()
    
    def cancel(self):
        """取消"""
        self.result = None
        self.destroy()
    
    def center_window(self):
        """窗口居中"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

