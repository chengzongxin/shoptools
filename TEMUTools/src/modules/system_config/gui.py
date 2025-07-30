import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from .config import SystemConfig

class SystemConfigTab(ttk.Frame):
    """系统配置标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.config = SystemConfig()
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 商家中心Cookie配置区域
        seller_frame = ttk.LabelFrame(main_frame, text="商家中心配置", padding="10")
        seller_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(seller_frame, text="商家中心Cookie:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.seller_cookie_text = tk.Text(seller_frame, height=3, width=60)
        self.seller_cookie_text.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        self.seller_cookie_text.insert('1.0', self.config.get_seller_cookie())
        
        # 商家中心按钮
        ttk.Button(seller_frame, text="获取Cookie", 
                  command=self._get_seller_cookie).grid(row=2, column=0, pady=5, padx=2, sticky=tk.W)
        ttk.Button(seller_frame, text="测试API", 
                  command=self._test_seller_api).grid(row=2, column=1, pady=5, padx=2, sticky=tk.W)
        ttk.Button(seller_frame, text="清空", 
                  command=lambda: self._clear_text(self.seller_cookie_text)).grid(row=2, column=2, pady=5, padx=2, sticky=tk.W)
        
        # 合规中心Cookie配置区域
        compliance_frame = ttk.LabelFrame(main_frame, text="合规中心配置", padding="10")
        compliance_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(compliance_frame, text="合规中心Cookie:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.compliance_cookie_text = tk.Text(compliance_frame, height=3, width=60)
        self.compliance_cookie_text.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        self.compliance_cookie_text.insert('1.0', self.config.get_compliance_cookie())
        
        # 合规中心按钮
        ttk.Button(compliance_frame, text="获取Cookie", 
                  command=self._get_compliance_cookie).grid(row=2, column=0, pady=5, padx=2, sticky=tk.W)
        ttk.Button(compliance_frame, text="测试API", 
                  command=self._test_compliance_api).grid(row=2, column=1, pady=5, padx=2, sticky=tk.W)
        ttk.Button(compliance_frame, text="清空", 
                  command=lambda: self._clear_text(self.compliance_cookie_text)).grid(row=2, column=2, pady=5, padx=2, sticky=tk.W)
        
        # MallID配置区域
        mallid_frame = ttk.LabelFrame(main_frame, text="MallID配置", padding="10")
        mallid_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(mallid_frame, text="MallID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.mallid_entry = ttk.Entry(mallid_frame, width=50)
        self.mallid_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.mallid_entry.insert(0, self.config.get_mallid())
        
        # 主要操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="保存所有配置", 
                  command=self._save_config).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="清空所有配置", 
                  command=self._clear_all_config).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="测试所有API", 
                  command=self._test_all_apis).grid(row=0, column=2, padx=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        seller_frame.columnconfigure(0, weight=1)
        compliance_frame.columnconfigure(0, weight=1)
        mallid_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._log("系统配置页面已初始化")
    
    def _log(self, message: str):
        """添加日志消息"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def _clear_text(self, text_widget):
        """清空文本框"""
        text_widget.delete('1.0', tk.END)
    
    def _get_seller_cookie(self):
        """获取商家中心Cookie"""
        def get_cookie():
            self._log("正在从浏览器获取商家中心Cookie...")
            cookie_string, error_msg = self.config.get_seller_cookie_from_browser()
            
            if error_msg:
                self._log(f"❌ 获取失败: {error_msg}")
                messagebox.showerror("获取失败", error_msg)
            else:
                self.seller_cookie_text.delete('1.0', tk.END)
                self.seller_cookie_text.insert('1.0', cookie_string)
                self._log(f"✅ 商家中心Cookie获取成功，长度: {len(cookie_string)} 字符")
                messagebox.showinfo("获取成功", "商家中心Cookie已自动填入，请点击保存配置")
        
        # 在后台线程中执行，避免界面卡顿
        threading.Thread(target=get_cookie, daemon=True).start()
    
    def _get_compliance_cookie(self):
        """获取合规中心Cookie"""
        def get_cookie():
            self._log("正在从浏览器获取合规中心Cookie...")
            cookie_string, error_msg = self.config.get_compliance_cookie_from_browser()
            
            if error_msg:
                self._log(f"❌ 获取失败: {error_msg}")
                messagebox.showerror("获取失败", error_msg)
            else:
                self.compliance_cookie_text.delete('1.0', tk.END)
                self.compliance_cookie_text.insert('1.0', cookie_string)
                self._log(f"✅ 合规中心Cookie获取成功，长度: {len(cookie_string)} 字符")
                messagebox.showinfo("获取成功", "合规中心Cookie已自动填入，请点击保存配置")
        
        # 在后台线程中执行，避免界面卡顿
        threading.Thread(target=get_cookie, daemon=True).start()
    
    def _test_seller_api(self):
        """测试商家中心API"""
        def test_api():
            self._log("正在测试商家中心API...")
            cookie = self.seller_cookie_text.get('1.0', tk.END).strip()
            
            success, message, result = self.config.test_seller_api(cookie)
            
            if success:
                self._log(message)
                # 如果API测试成功且返回了mallId，自动填入
                if result and result.get('result', {}).get('mallList'):
                    for mall in result['result']['mallList']:
                        mall_id = str(mall.get('mallId', ''))
                        if mall_id and mall_id != 'None':
                            # 使用 self.after() 在主线程中操作GUI组件
                            def update_mall_id():
                                self.mallid_entry.delete(0, tk.END)
                                self.mallid_entry.insert(0, mall_id)
                            self.after(0, update_mall_id)
                            self._log(f"✅ 自动获取到MallID: {mall_id}")
                            break
                # 使用 self.after() 在主线程中显示消息框
                self.after(0, lambda: messagebox.showinfo("测试成功", message))
            else:
                self._log(f"❌ {message}")
                # 使用 self.after() 在主线程中显示错误消息框
                self.after(0, lambda: messagebox.showerror("测试失败", message))
        
        # 在后台线程中执行，避免界面卡顿
        threading.Thread(target=test_api, daemon=True).start()
    
    def _test_compliance_api(self):
        """测试合规中心API"""
        def test_api():
            self._log("正在测试合规中心API...")
            cookie = self.compliance_cookie_text.get('1.0', tk.END).strip()
            
            success, message, result = self.config.test_compliance_api(cookie)
            
            if success:
                self._log(message)
                # 使用 self.after() 在主线程中显示消息框
                self.after(0, lambda: messagebox.showinfo("测试成功", message))
            else:
                self._log(f"❌ {message}")
                # 使用 self.after() 在主线程中显示错误消息框
                self.after(0, lambda: messagebox.showerror("测试失败", message))
        
        # 在后台线程中执行，避免界面卡顿
        threading.Thread(target=test_api, daemon=True).start()
    
    def _test_all_apis(self):
        """测试所有API"""
        def test_all():
            self._log("开始测试所有API...")
            
            # 测试商家中心API
            seller_cookie = self.seller_cookie_text.get('1.0', tk.END).strip()
            if seller_cookie:
                success, message, result = self.config.test_seller_api(seller_cookie)
                if success:
                    self._log(f"✅ 商家中心: {message}")
                else:
                    self._log(f"❌ 商家中心: {message}")
            else:
                self._log("⚠️ 商家中心Cookie为空，跳过测试")
            
            # 测试合规中心API
            compliance_cookie = self.compliance_cookie_text.get('1.0', tk.END).strip()
            if compliance_cookie:
                success, message, result = self.config.test_compliance_api(compliance_cookie)
                if success:
                    self._log(f"✅ 合规中心: {message}")
                else:
                    self._log(f"❌ 合规中心: {message}")
            else:
                self._log("⚠️ 合规中心Cookie为空，跳过测试")
            
            self._log("所有API测试完成")
        
        # 在后台线程中执行，避免界面卡顿
        threading.Thread(target=test_all, daemon=True).start()
        
    def _save_config(self):
        """保存配置"""
        try:
            seller_cookie = self.seller_cookie_text.get('1.0', tk.END).strip()
            compliance_cookie = self.compliance_cookie_text.get('1.0', tk.END).strip()
            mallid = self.mallid_entry.get().strip()
            
            self.config.update_config(
                seller_cookie=seller_cookie,
                compliance_cookie=compliance_cookie,
                mallid=mallid
            )
            
            self._log("✅ 配置已保存")
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            error_msg = f"保存配置失败: {str(e)}"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
            
    def _clear_all_config(self):
        """清空所有配置"""
        if messagebox.askyesno("确认", "确定要清空所有配置吗？"):
            self.seller_cookie_text.delete('1.0', tk.END)
            self.compliance_cookie_text.delete('1.0', tk.END)
            self.mallid_entry.delete(0, tk.END)
            self.config.update_config("", "", "")
            self._log("✅ 所有配置已清空")
            messagebox.showinfo("成功", "所有配置已清空") 