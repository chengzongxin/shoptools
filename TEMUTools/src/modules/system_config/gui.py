import tkinter as tk
from tkinter import ttk, messagebox
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
        
        # 商家中心Cookie
        ttk.Label(main_frame, text="商家中心Cookie:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.seller_cookie_text = tk.Text(main_frame, height=3, width=50)
        self.seller_cookie_text.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.seller_cookie_text.insert('1.0', self.config.get_seller_cookie())
        
        # 合规Cookie
        ttk.Label(main_frame, text="合规Cookie:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.compliance_cookie_text = tk.Text(main_frame, height=3, width=50)
        self.compliance_cookie_text.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.compliance_cookie_text.insert('1.0', self.config.get_compliance_cookie())
        
        # MallID
        ttk.Label(main_frame, text="MallID:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.mallid_entry = ttk.Entry(main_frame, width=50)
        self.mallid_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.mallid_entry.insert(0, self.config.get_mallid())
        
        # 保存按钮
        save_button = ttk.Button(main_frame, text="保存配置", command=self._save_config)
        save_button.grid(row=3, column=1, pady=10)
        
        # 清空按钮
        clear_button = ttk.Button(main_frame, text="清空", command=self._clear_config)
        clear_button.grid(row=3, column=2, pady=10)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
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
            
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            
    def _clear_config(self):
        """清空配置"""
        if messagebox.askyesno("确认", "确定要清空所有配置吗？"):
            self.seller_cookie_text.delete('1.0', tk.END)
            self.compliance_cookie_text.delete('1.0', tk.END)
            self.mallid_entry.delete(0, tk.END)
            self.config.update_config("", "", "")
            messagebox.showinfo("成功", "配置已清空") 