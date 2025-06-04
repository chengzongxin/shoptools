import sys
import os
import traceback
from modules.common.browser_manager import BrowserManager
from modules.price.price_review import PriceReview
from modules.compliance.compliance_review import ComplianceReview
from config import DEBUG

def show_menu():
    """
    显示功能选择菜单
    """
    print("\n" + "="*50)
    print("跨境电商自动化工具")
    print("="*50)
    print("请选择要执行的功能：")
    print("1. 价格审核")
    print("2. 合规审核")
    print("0. 退出程序")
    print("="*50)
    
    while True:
        try:
            choice = input("请输入选项编号（0-2）: ").strip()
            if choice in ['0', '1', '2']:
                return int(choice)
            print("无效的选项，请重新输入！")
        except ValueError:
            print("请输入有效的数字！")

def run_price_review(browser_manager):
    """
    运行价格审核功能
    """
    try:
        print("\n开始执行价格审核...")
        price_review = PriceReview(browser_manager.driver, browser_manager.wait, DEBUG)
        price_review.start_review()
        print("价格审核完成！")
    except Exception as e:
        print(f"价格审核执行失败: {str(e)}")
        raise

def run_compliance_review(browser_manager):
    """
    运行合规审核功能
    """
    try:
        print("\n开始执行合规审核...")
        compliance_review = ComplianceReview(browser_manager, debug=True)
        compliance_review.start_review()
        print("合规审核完成！")
    except Exception as e:
        print(f"合规审核执行失败: {str(e)}")
        raise

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
        
        # 创建浏览器管理器实例
        print("正在初始化浏览器管理器...")
        browser_manager = BrowserManager(debug=True)
        
        while True:
            # 显示菜单并获取用户选择
            choice = show_menu()
            
            if choice == 0:
                print("\n感谢使用，再见！")
                break
            elif choice == 1:
                run_price_review(browser_manager)
            elif choice == 2:
                run_compliance_review(browser_manager)
            
            # 询问是否继续
            if input("\n是否继续执行其他功能？(y/n): ").lower() != 'y':
                print("\n感谢使用，再见！")
                break
            
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