import sys
import os
from modules.browser_manager import BrowserManager
from modules.price_review import PriceReview
from config import DEBUG

def main():
    """
    主函数
    负责初始化和协调各个模块的工作
    """
    browser_manager = None
    try:
        if DEBUG:
            print("开始创建自动化实例...")
            print(f"当前工作目录: {os.getcwd()}")
            print(f"Python版本: {sys.version}")
        
        # 创建浏览器管理器实例
        browser_manager = BrowserManager(DEBUG)
        
        # 创建价格审核实例
        price_review = PriceReview(browser_manager.driver, browser_manager.wait, DEBUG)
        
        # 开始价格审核流程
        price_review.start_review()
        
        if DEBUG:
            print("自动化操作完成！")
            
    except Exception as e:
        print(f"发生错误：{str(e)}")
        print(f"错误类型：{type(e).__name__}")
        print(f"错误详情：{sys.exc_info()}")
    finally:
        # 确保浏览器被正确关闭
        if browser_manager:
            browser_manager.close()

if __name__ == "__main__":
    main() 