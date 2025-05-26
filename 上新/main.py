import sys
import os
import traceback
from modules.browser_manager import BrowserManager
from modules.price_review import PriceReview
from config import DEBUG

def get_resource_path(relative_path):
    """
    获取资源的绝对路径，支持开发环境和打包后的环境
    """
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def main():
    """
    主函数
    负责初始化和协调各个模块的工作
    """
    browser_manager = None
    try:
        print("="*50)
        print("程序开始运行...")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"Python版本: {sys.version}")
        print("="*50)
        
        # 获取chromedriver路径
        chromedriver_path = get_resource_path(os.path.join("drivers", "chromedriver.exe"))
        print(f"ChromeDriver路径: {chromedriver_path}")
        print(f"ChromeDriver是否存在: {os.path.exists(chromedriver_path)}")
        
        # 创建浏览器管理器实例
        print("正在初始化浏览器管理器...")
        browser_manager = BrowserManager(DEBUG, chromedriver_path)
        
        # 创建价格审核实例
        print("正在初始化价格审核模块...")
        price_review = PriceReview(browser_manager.driver, browser_manager.wait, DEBUG)
        
        # 开始价格审核流程
        print("开始执行价格审核流程...")
        price_review.start_review()
        
        print("="*50)
        print("自动化操作完成！")
        print("="*50)
            
    except Exception as e:
        print("="*50)
        print("程序发生错误！")
        print(f"错误信息：{str(e)}")
        print(f"错误类型：{type(e).__name__}")
        print("详细错误信息：")
        traceback.print_exc()
        print("="*50)
        
        # 等待用户输入，防止窗口立即关闭
        input("按回车键退出...")
    finally:
        # 确保浏览器被正确关闭
        if browser_manager:
            try:
                browser_manager.close()
            except Exception as e:
                print(f"关闭浏览器时发生错误：{str(e)}")

if __name__ == "__main__":
    main() 