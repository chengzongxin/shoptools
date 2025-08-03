import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from .config import SystemConfig

class SystemConfigTab(ttk.Frame):
    """系统配置标签页"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.config = SystemConfig()
        self.status_update_thread = None
        self.status_update_running = True
        self._init_ui()
        self._start_status_update()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # TEMU Cookie配置区域
        cookie_frame = ttk.LabelFrame(main_frame, text="TEMU Cookie配置", padding="10")
        cookie_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(cookie_frame, text="TEMU Cookie (agentseller.temu.com):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cookie_text = tk.Text(cookie_frame, height=3, width=60)
        self.cookie_text.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=2)
        self.cookie_text.insert('1.0', self.config.get_cookie())
        
        # Cookie操作按钮
        ttk.Button(cookie_frame, text="获取Cookie(浏览器)", 
                  command=self._get_cookie).grid(row=2, column=0, pady=5, padx=2, sticky=tk.W)
        ttk.Button(cookie_frame, text="获取Cookie(插件)", 
                  command=self._get_cookie_websocket).grid(row=2, column=1, pady=5, padx=2, sticky=tk.W)
        ttk.Button(cookie_frame, text="测试API", 
                  command=self._test_api).grid(row=2, column=2, pady=5, padx=2, sticky=tk.W)
        ttk.Button(cookie_frame, text="清空", 
                  command=lambda: self._clear_text(self.cookie_text)).grid(row=2, column=3, pady=5, padx=2, sticky=tk.W)
        
        # MallID配置区域
        mallid_frame = ttk.LabelFrame(main_frame, text="MallID配置", padding="10")
        mallid_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(mallid_frame, text="MallID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.mallid_entry = ttk.Entry(mallid_frame, width=50)
        self.mallid_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.mallid_entry.insert(0, self.config.get_mallid())
        
        # 主要操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="保存所有配置", 
                  command=self._save_config).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="清空所有配置", 
                  command=self._clear_all_config).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="测试API连接", 
                  command=self._test_api).grid(row=0, column=2, padx=5)

         # WebSocket连接状态区域
        status_frame = ttk.LabelFrame(main_frame, text="WebSocket连接状态", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 状态指示器
        self.status_label = ttk.Label(status_frame, text="正在检查连接状态...", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # 状态图标（使用文本符号作为简单的状态指示器）
        self.status_icon = ttk.Label(status_frame, text="⏳", font=("Arial", 12))
        self.status_icon.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # 连接信息
        self.connection_info = ttk.Label(status_frame, text="", font=("Arial", 9))
        self.connection_info.grid(row=0, column=2, pady=2)
        
        # WebSocket控制按钮
        # ttk.Button(status_frame, text="启动WebSocket服务器", 
        #           command=self._start_websocket_server).grid(row=2, column=0, pady=5, padx=2, sticky=tk.W)
        # ttk.Button(status_frame, text="停止WebSocket服务器", 
        #           command=self._stop_websocket_server).grid(row=2, column=2, pady=5, padx=2, sticky=tk.W)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        status_frame.columnconfigure(0, weight=1)
        cookie_frame.columnconfigure(0, weight=1)
        mallid_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self._log("系统配置页面已初始化")
    
    def _start_status_update(self):
        """启动状态更新线程"""
        def update_status():
            while self.status_update_running:
                try:
                    # 在主线程中更新UI
                    self.after(0, self._update_websocket_status)
                    time.sleep(2)  # 每2秒更新一次状态
                except Exception as e:
                    print(f"状态更新错误: {e}")
                    time.sleep(5)  # 出错时等待更长时间
        
        self.status_update_thread = threading.Thread(target=update_status, daemon=True)
        self.status_update_thread.start()
    
    def _update_websocket_status(self):
        """更新WebSocket连接状态显示"""
        try:
            from .websocket_cookie import is_connected, is_running, connected_clients
            
            # 检查服务器是否运行
            if not is_running:
                self.status_label.config(text="WebSocket服务器未运行", foreground="red")
                self.status_icon.config(text="❌", foreground="red")
                self.connection_info.config(text="服务器状态: 已停止")
                return
            
            # 检查是否有连接的客户端
            if is_connected():
                client_count = len(connected_clients)
                self.status_label.config(text=f"WebSocket已连接 ({client_count} 个客户端)", foreground="green")
                self.status_icon.config(text="✅", foreground="green")
                self.connection_info.config(text=f"服务器状态: 运行中 | 连接数: {client_count}")
            else:
                self.status_label.config(text="WebSocket服务器运行中，等待连接...", foreground="orange")
                self.status_icon.config(text="⏳", foreground="orange")
                self.connection_info.config(text="服务器状态: 运行中 | 连接数: 0")
                
        except ImportError:
            self.status_label.config(text="WebSocket模块未安装", foreground="red")
            self.status_icon.config(text="❌", foreground="red")
            self.connection_info.config(text="请安装websockets依赖")
        except Exception as e:
            self.status_label.config(text="状态检查失败", foreground="red")
            self.status_icon.config(text="❌", foreground="red")
            self.connection_info.config(text=f"错误: {str(e)}")
    
    def _start_websocket_server(self):
        """启动WebSocket服务器"""
        try:
            from .websocket_cookie import start_websocket_server
            start_websocket_server()
            self._log("✅ WebSocket服务器已启动")
            messagebox.showinfo("成功", "WebSocket服务器已启动，请确保Chrome插件已连接")
        except ImportError:
            error_msg = "WebSocket模块未安装，请安装websockets依赖"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
        except Exception as e:
            error_msg = f"启动WebSocket服务器失败: {str(e)}"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
    
    def _stop_websocket_server(self):
        """停止WebSocket服务器"""
        try:
            from .websocket_cookie import stop_websocket_server
            stop_websocket_server()
            self._log("✅ WebSocket服务器已停止")
            messagebox.showinfo("成功", "WebSocket服务器已停止")
        except ImportError:
            error_msg = "WebSocket模块未安装"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
        except Exception as e:
            error_msg = f"停止WebSocket服务器失败: {str(e)}"
            self._log(f"❌ {error_msg}")
            messagebox.showerror("错误", error_msg)
    
    def _log(self, message: str):
        """添加日志消息"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def _clear_text(self, text_widget):
        """清空文本框"""
        text_widget.delete('1.0', tk.END)
    
    def _get_cookie(self):
        """获取TEMU Cookie"""
        def get_cookie():
            self._log("正在从浏览器获取TEMU Cookie...")
            cookie_string, error_msg = self.config.get_cookie_from_browser()
            
            if error_msg:
                self._log(f"❌ 获取失败: {error_msg}")
                messagebox.showerror("获取失败", error_msg)
            else:
                self.cookie_text.delete('1.0', tk.END)
                self.cookie_text.insert('1.0', cookie_string)
                self._log(f"✅ TEMU Cookie获取成功，长度: {len(cookie_string)} 字符")
                messagebox.showinfo("获取成功", "TEMU Cookie已自动填入，请点击保存配置")
        
        # 在后台线程中执行，避免界面卡顿
        threading.Thread(target=get_cookie, daemon=True).start()
    
    def _get_cookie_websocket(self):
        """通过WebSocket从Chrome插件获取Cookie"""
        def get_cookie_ws():
            self._log("正在通过Chrome插件获取TEMU Cookie...")
            cookie_string, error_msg = self.config.get_cookie_from_websocket()
            
            if error_msg:
                self._log(f"❌ 获取失败: {error_msg}")
                # 使用 self.after() 在主线程中显示错误消息框
                self.after(0, lambda: messagebox.showerror("获取失败", error_msg))
            else:
                # 使用 self.after() 在主线程中更新GUI
                def update_cookie():
                    self.cookie_text.delete('1.0', tk.END)
                    self.cookie_text.insert('1.0', cookie_string)
                self.after(0, update_cookie)
                self._log(f"✅ Chrome插件Cookie获取成功，长度: {len(cookie_string)} 字符")
                # 使用 self.after() 在主线程中显示成功消息框
                self.after(0, lambda: messagebox.showinfo("获取成功", "Chrome插件Cookie已自动填入，请点击保存配置"))
        
        # 在后台线程中执行，避免界面卡顿
        threading.Thread(target=get_cookie_ws, daemon=True).start()
    
    def _test_api(self):
        """测试API连接"""
        def test_api():
            self._log("正在测试API连接...")
            cookie = self.cookie_text.get('1.0', tk.END).strip()
            
            success, message, result = self.config.test_api(cookie)
            
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
        
    def _save_config(self):
        """保存配置"""
        try:
            cookie = self.cookie_text.get('1.0', tk.END).strip()
            mallid = self.mallid_entry.get().strip()
            
            self.config.update_config(
                cookie=cookie,
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
            self.cookie_text.delete('1.0', tk.END)
            self.mallid_entry.delete(0, tk.END)
            self.config.update_config("", "")
            self._log("✅ 所有配置已清空")
            messagebox.showinfo("成功", "所有配置已清空")
    
    def destroy(self):
        """销毁组件时清理资源"""
        # 停止状态更新线程
        self.status_update_running = False
        if hasattr(self, 'status_update_thread') and self.status_update_thread:
            # 等待线程结束（最多等待1秒）
            self.status_update_thread.join(timeout=1.0)
        
        # 调用父类的销毁方法
        super().destroy() 