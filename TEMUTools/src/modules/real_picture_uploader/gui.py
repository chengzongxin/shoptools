import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
import os
import sys
from datetime import datetime
from .crawler import RealPictureUploader

class RealPictureUploaderTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.setup_logging()

    def setup_ui(self):
        """设置用户界面"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建说明标签
        info_frame = ttk.LabelFrame(main_frame, text="功能说明", padding="5")
        info_frame.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        info_text = """
        实拍图批量上传功能说明：
        1. 支持8个品类的商品实拍图批量上传
        2. 自动查询未上传实拍图的商品
        3. 按品类依次处理，每个品类处理完成后自动进入下一个
        4. 包含随机延迟，模拟人工操作
        5. 请确保assets/images目录下有对应的图片文件
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # 创建品类选择框架
        category_frame = ttk.LabelFrame(main_frame, text="品类选择", padding="5")
        category_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # 品类列表
        self.categories = [
            "抽绳健身包", "帆布袋", "冰袖", "头带", 
            "头巾", "袜子", "围裙", "抱枕"
        ]
        
        self.category_vars = {}
        for i, category in enumerate(self.categories):
            var = tk.BooleanVar(value=True)  # 默认全选
            self.category_vars[category] = var
            ttk.Checkbutton(
                category_frame, 
                text=category, 
                variable=var
            ).grid(row=i//4, column=i%4, sticky=tk.W, padx=5)
            
        # 全选/取消全选按钮
        ttk.Button(
            category_frame, 
            text="全选", 
            command=self.select_all_categories
        ).grid(row=len(self.categories)//4 + 1, column=0, pady=5)
        
        ttk.Button(
            category_frame, 
            text="取消全选", 
            command=self.deselect_all_categories
        ).grid(row=len(self.categories)//4 + 1, column=1, pady=5)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="开始批量上传", 
            command=self.start_upload
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="停止", 
            command=self.stop_upload, 
            state='disabled'
        )
        self.stop_button.grid(row=0, column=1, padx=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100
        )
        self.progress_bar.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        # 日志显示
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=15, width=100, state='disabled')
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 配置网格权重
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def setup_logging(self):
        """设置日志处理器"""
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, msg + '\n')
                    self.text_widget.see(tk.END)
                    self.text_widget.configure(state='disabled')
                self.text_widget.after(0, append)
        
        self.logger = logging.getLogger('real_picture_uploader')
        self.logger.setLevel(logging.INFO)
        
        # 移除所有现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # 添加文本处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(text_handler)
        
        # 添加文件处理器
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'real_picture_upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        self.logger.info("实拍图批量上传工具已初始化")
        self.logger.info(f"日志文件保存在: {log_file}")

    def select_all_categories(self):
        """全选所有品类"""
        for var in self.category_vars.values():
            var.set(True)
        self.logger.info("已全选所有品类")

    def deselect_all_categories(self):
        """取消全选所有品类"""
        for var in self.category_vars.values():
            var.set(False)
        self.logger.info("已取消全选所有品类")

    def start_upload(self):
        """开始上传"""
        # 检查是否有选中的品类
        selected_categories = [name for name, var in self.category_vars.items() if var.get()]
        if not selected_categories:
            messagebox.showwarning("警告", "请至少选择一个品类！")
            return
            
        # 检查图片文件是否存在
        if getattr(sys, 'frozen', False):
            # The application is frozen (packaged)
            base_path = sys._MEIPASS
        else:
            # The application is running from source
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        images_dir = os.path.join(base_path, 'assets', 'images')
        if not os.path.exists(images_dir):
            messagebox.showerror("错误", f"图片目录不存在: {images_dir}\n请在程序根目录创建 assets/images 文件夹，并放入所需图片。")
            return

        # 根据选择的品类，检查对应的图片文件
        temp_uploader = RealPictureUploader(logger=self.logger)
        all_category_configs = temp_uploader.categories
        
        required_images = set()
        for cat_name in selected_categories:
            for cat_config in all_category_configs:
                if cat_config['name'] == cat_name:
                    required_images.add(cat_config['image_file'])
        
        missing_images = []
        for image_name in required_images:
            image_path = os.path.join(images_dir, image_name)
            if not os.path.exists(image_path):
                missing_images.append(image_name)
                
        if missing_images:
            messagebox.showerror("错误", f"缺少以下图片文件:\n{', '.join(missing_images)}\n\n请将它们放置在 {images_dir} 目录下。")
            return
            
        # 更新UI状态
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_var.set(0)
        
        # 创建上传器
        self.uploader = RealPictureUploader(
            logger=self.logger,
            progress_callback=self.update_progress,
            stop_flag_callback=lambda: self._stop_flag
        )
        
        # 过滤选中的品类
        self.uploader.categories = [
            cat for cat in self.uploader.categories 
            if cat['name'] in selected_categories
        ]
        
        self.logger.info(f"开始批量上传，选中品类: {', '.join(selected_categories)}")
        
        # 设置停止标志
        self._stop_flag = False
        
        # 在新线程中运行上传
        self.upload_thread = threading.Thread(target=self.run_upload)
        self.upload_thread.start()

    def run_upload(self):
        """在新线程中运行上传"""
        try:
            self.uploader.batch_upload_all()
            if not self._stop_flag:
                self.after(0, lambda: messagebox.showinfo("完成", "所有实拍图已批量上传完成！"))
        except Exception as e:
            import traceback
            self.logger.error(f"批量上传失败: {str(e)}")
            self.logger.error(traceback.format_exc())
            if not self._stop_flag:
                self.after(0, lambda: messagebox.showerror("错误", f"批量上传失败: {str(e)}"))
        finally:
            self.after(0, lambda: self.start_button.config(state='normal'))
            self.after(0, lambda: self.stop_button.config(state='disabled'))

    def stop_upload(self):
        """停止上传"""
        self._stop_flag = True
        self.logger.info("用户请求停止上传")
        messagebox.showinfo("提示", "正在停止上传，请稍候...")

    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value) 