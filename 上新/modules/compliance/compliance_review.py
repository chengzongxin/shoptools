from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
from datetime import datetime
import os
from ..common.logger import Logger
from ..common.browser_manager import BrowserManager

class ComplianceReview:
    """
    合规审核类
    负责处理合规相关的自动化操作
    """
    def __init__(self, browser_manager: BrowserManager, debug=True):
        """
        初始化合规审核类
        :param browser_manager: 浏览器管理器实例
        :param debug: 是否开启调试模式
        """
        self.browser = browser_manager
        self.logger = Logger("compliance", debug)
        self.debug = debug

    def switch_to_new_tab(self, timeout=10):
        """
        切换到新打开的标签页
        :param timeout: 等待超时时间（秒）
        :return: 是否成功切换到新标签页
        """
        try:
            # 记录当前标签页数量
            original_handles = self.browser.driver.window_handles
            
            # 等待新标签页打开
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_handles = self.browser.driver.window_handles
                if len(current_handles) > len(original_handles):
                    # 找到新打开的标签页
                    new_handle = [handle for handle in current_handles if handle not in original_handles][0]
                    # 切换到新标签页
                    self.browser.driver.switch_to.window(new_handle)
                    self.logger.info("已切换到新标签页")
                    return True
                time.sleep(0.5)
            
            self.logger.error("等待新标签页超时")
            return False
            
        except Exception as e:
            self.logger.error(f"切换到新标签页失败: {str(e)}")
            return False

    def check_and_close_popup(self):
        """
        检查并关闭弹窗
        :return: 是否发现并关闭了弹窗
        """
        try:
            # 检查是否存在弹窗标题
            popup_title = self.browser.driver.find_elements(By.CLASS_NAME, 'PP_popoverTitle_5-114-0')
            
            if popup_title:
                if self.debug:
                    print("发现弹窗，准备关闭...")
                
                # 点击关闭按钮
                close_button = self.browser.wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'new-bell_container__eWEgQ'))
                )
                close_button.click()
                
                # 等待弹窗消失
                time.sleep(1)
                
                if self.debug:
                    print("弹窗已关闭")
                
                return True
            
            return False

        except Exception as e:
            print(f"检查或关闭弹窗失败: {str(e)}")
            return False

    def click_compliance_pending_button(self):
        """
        点击合规待确认按钮
        """
        try:
            # 首先检查并关闭可能存在的弹窗
            self.check_and_close_popup()

            if self.debug:
                print("正在查找合规待确认按钮...")

            # 使用CSS选择器定位按钮
            button = self.browser.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#root > div > div > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)'))
            )
            
            # 获取按钮文本（包含商品数量）
            button_text = button.text
            if self.debug:
                print(f"找到合规待确认按钮: {button_text}")

            # 点击按钮
            button.click()
            
            if self.debug:
                print("成功点击合规待确认按钮")
            
            return True

        except Exception as e:
            print(f"点击合规待确认按钮失败: {str(e)}")
            return False

    def start_review(self):
        """
        开始合规审核流程
        """
        try:
            self.logger.info("开始合规审核流程")
            
            # 1. 打开首页
            self.logger.info("正在打开首页...")
            self.browser.driver.get("https://seller.kuajingmaihuo.com/main/product/seller-select")
            time.sleep(3)  # 等待页面加载
            
            # 2. 点击合规中心链接
            self.logger.info("正在查找合规中心链接...")
            compliance_link = self.browser.wait.until(
                lambda driver: driver.find_element("css selector", 
                    "a[data-report-click-text='合规中心']")
            )
            compliance_link.click()
            self.logger.info("已点击合规中心链接")
            
            # 3. 处理授权弹窗
            self.logger.info("正在处理授权弹窗...")
            auth_button = self.browser.wait.until(
                lambda driver: driver.find_element("css selector", 
                    "button.BTN_outerWrapper_5-114-0.BTN_primary_5-114-0.BTN_large_5-114-0.BTN_outerWrapperBtn_5-114-0")
            )
            auth_button.click()
            self.logger.info("已点击授权确认按钮")
            
            # 4. 切换到新标签页
            if not self.switch_to_new_tab():
                raise Exception("无法切换到新标签页")
            
            # 5. 等待新页面加载完成
            self.logger.info("等待新页面加载...")
            time.sleep(3)
            
            # 6. 查找并点击商品合规信息菜单
            self.logger.info("正在查找商品合规信息菜单...")
            menu_item = self.browser.wait.until(
                lambda driver: driver.find_element("xpath", 
                    "//ul[contains(@class, 'rocket-menu') and contains(@class, 'rocket-menu-dark') and contains(@class, 'rocket-menu-root') and contains(@class, 'rocket-menu-inline')]//li[@title='商品合规信息']")
            )
            menu_item.click()
            self.logger.info("已点击商品合规信息菜单")
            
            # 7. 等待页面加载并点击批量上传按钮
            self.logger.info("等待页面加载...")
            time.sleep(3)
            
            self.logger.info("正在查找批量上传按钮...")
            upload_button = self.browser.wait.until(
                lambda driver: driver.find_element("xpath", 
                    "//*[@id='agentseller-layout-content']/div/div/div/button[1]")
            )
            upload_button.click()
            self.logger.info("已点击批量上传按钮")
            
            # 等待侧边栏出现
            time.sleep(2)
            
            # 8. 选择合规信息类型
            self.logger.info("正在查找合规信息类型输入框...")
            input_box = self.browser.wait.until(
                lambda driver: driver.find_element("css selector", 
                    "input.rocket-select-selection-search-input")
            )
            # 使用JavaScript点击来避免元素被遮挡
            self.browser.driver.execute_script("arguments[0].click();", input_box)
            self.logger.info("已点击输入框")
            
            # 等待选项列表出现
            time.sleep(1)
            
            # 选择"加利福尼亚州65号法案"选项
            self.logger.info("正在选择合规信息类型...")
            option = self.browser.wait.until(
                lambda driver: driver.find_element("xpath", 
                    "//div[contains(@class, 'rocket-select-item-option-content') and contains(text(), '加利福尼亚州65号法案')]")
            )
            # 使用JavaScript点击选项
            self.browser.driver.execute_script("arguments[0].click();", option)
            self.logger.info("已选择加利福尼亚州65号法案")
            
        except Exception as e:
            self.logger.error(f"合规审核流程出错: {str(e)}")
            raise 