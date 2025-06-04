import os
from datetime import datetime

class Logger:
    def __init__(self, module_name, debug=True):
        """
        初始化日志管理器
        :param module_name: 模块名称
        :param debug: 是否开启调试模式
        """
        self.module_name = module_name
        self.debug = debug
        
        # 创建日志目录
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 创建日志文件（使用日期作为文件名）
        self.log_file = os.path.join(self.log_dir, f"{module_name}_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 如果文件不存在，添加表头
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write(f"{module_name} 日志 - {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write("=" * 80 + "\n\n")

    def info(self, message):
        """
        记录信息日志
        :param message: 日志信息
        """
        self.log_record(message=message, level="INFO")

    def error(self, message):
        """
        记录错误日志
        :param message: 错误信息
        """
        self.log_error(message)

    def log_record(self, **kwargs):
        """
        记录日志
        :param kwargs: 要记录的键值对
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] "
            
            # 添加所有键值对到日志
            for key, value in kwargs.items():
                log_entry += f"{key}: {value}, "
            
            # 移除最后的逗号和空格
            log_entry = log_entry.rstrip(", ") + "\n"
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
            if self.debug:
                print(f"已记录日志: {log_entry.strip()}")
                
        except Exception as e:
            print(f"记录日志失败: {str(e)}")

    def log_error(self, error_msg, **kwargs):
        """
        记录错误日志
        :param error_msg: 错误信息
        :param kwargs: 其他要记录的键值对
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [ERROR] {error_msg}\n"
            
            # 添加其他信息
            if kwargs:
                log_entry += "详细信息:\n"
                for key, value in kwargs.items():
                    log_entry += f"  {key}: {value}\n"
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
            if self.debug:
                print(f"已记录错误日志: {log_entry.strip()}")
                
        except Exception as e:
            print(f"记录错误日志失败: {str(e)}") 