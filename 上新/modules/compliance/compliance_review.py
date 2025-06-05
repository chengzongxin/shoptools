from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
from datetime import datetime
import os
from ..common.logger import Logger
from ..common.browser_manager import BrowserManager
from selenium.webdriver.common.action_chains import ActionChains

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
            time.sleep(3)
            
            form = self.browser.driver.find_element(By.CSS_SELECTOR, "form.rocket-form-field.rocket-form-field-horizontal.rocket-form-field-small")
            
            # 8. 选择合规信息类型
            self.logger.info("正在查找合规信息类型输入框...")
            try:
                element = form.find_element(By.XPATH, "//div[2]/div[2]/div/div/div")
                # 确保元素在视图中
                self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)
                
                # 尝试点击
                try:
                    element.click()
                    self.logger.info("已直接点击元素")
                except:
                    try:
                        # 如果直接点击失败，使用JavaScript点击
                        self.browser.driver.execute_script("arguments[0].click();", element)
                        self.logger.info("已使用JavaScript点击元素")
                    except:
                        # 如果JavaScript点击也失败，使用Actions链
                        actions = ActionChains(self.browser.driver)
                        actions.move_to_element(element).pause(1).click().perform()
                        self.logger.info("已使用Actions链点击元素")
                
                # 等待下拉框出现
                time.sleep(2)
                
                # 检查下拉框是否出现
                try:
                    dropdown = WebDriverWait(self.browser.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "rocket-select-dropdown"))
                    )
                    self.logger.info("下拉选项已出现")
                except:
                    self.logger.error("点击后未出现下拉选项")
                    raise
                
            except Exception as e:
                self.logger.error(f"点击合规信息类型输入框失败: {str(e)}")
                raise
            
            # 9. 选择"加利福尼亚州65号法案"选项
            self.logger.info("正在选择合规信息类型...")
            option = self.browser.wait.until(
                lambda driver: driver.find_element("xpath", 
                    "//div[contains(@class, 'rocket-select-item-option-content') and contains(text(), '加利福尼亚州65号法案')]")
            )
            # 使用JavaScript点击选项
            self.browser.driver.execute_script("arguments[0].click();", option)
            self.logger.info("已选择加利福尼亚州65号法案")
            
            # 10. 选择"待上传"选项
            self.logger.info("正在查找待上传选择框...")
            try:

                upload_select = form.find_element(By.XPATH, "//div[4]/div[3]/div/div[2]/div/div/div")

                # 使用XPath等待待上传选择框出现
                # upload_select = WebDriverWait(self.browser.driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, 
                #          /html/body/div[6]/div/div[2]/div/div/div[2]/form/div[4]/div[3]/div/div[2]/div/div/div
                #         "/html/body/div[5]/div/div[2]/div/div/div[2]/form/div[4]/div[3]/div/div[2]/div/div/div/div"))
                # )

                upload_select.click()
                self.logger.info("已点击待上传选择框")
                
                # 等待下拉选项出现
                time.sleep(2)
                
                # 选择"待上传"选项
                upload_option = WebDriverWait(self.browser.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, 
                        "//div[contains(@class, 'rocket-select-item-option-content') and contains(text(), '待上传')]"))
                )
                
                # 点击选项
                self.browser.driver.execute_script("arguments[0].click();", upload_option)
                self.logger.info("已选择待上传选项")
                
                try:
                    # 先滚动到drawer body底部
                    try:
                        # 找到rocket-drawer-body元素
                        drawer_body = self.browser.driver.find_element(By.CLASS_NAME, "rocket-drawer-body")
                        
                        # 滚动到drawer body底部
                        self.browser.driver.execute_script("""
                            var element = arguments[0];
                            var viewportHeight = window.innerHeight;
                            var elementTop = element.getBoundingClientRect().top;
                            var elementBottom = element.getBoundingClientRect().bottom;
                            var scrollAmount = elementBottom - viewportHeight;
                            window.scrollBy(0, scrollAmount);
                        """, drawer_body)
                        
                        self.logger.info("已将drawer body滚动到底部")
                        time.sleep(2)  # 等待滚动完成
                    except Exception as e:
                        self.logger.error(f"滚动drawer body失败: {str(e)}")
                        raise

                    # 点击输入框
                    try:
                        # 使用form表单的相对XPath定位输入框
                        input_element = form.find_element(By.XPATH, "//div[8]/div/div/div/div/div[2]/div[1]/div/div")
                        self.logger.info("找到输入框元素")
                        
                        # 点击输入框
                        input_element.click()
                        self.logger.info("已点击输入框")
                        time.sleep(1)

                        # 等待虚拟列表出现并选择特定选项
                        try:
                            # 等待虚拟列表容器出现
                            virtual_list = WebDriverWait(self.browser.driver, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, "rocket-virtual-list-holder-inner"))
                            )
                            
                            # 滚动虚拟列表到底部
                            self.browser.driver.execute_script("""
                                var element = arguments[0];
                                element.scrollTop = element.scrollHeight;
                            """, virtual_list)
                            self.logger.info("已将虚拟列表滚动到底部")
                            time.sleep(1)  # 等待滚动完成
                            
                            # 在虚拟列表中查找特定title的选项
                            warning_option = WebDriverWait(virtual_list, 10).until(
                                EC.element_to_be_clickable((By.XPATH, ".//div[@title='No Warning Applicable/无需警示']"))
                            )
                            
                            # 点击选项
                            warning_option.click()
                            self.logger.info("已选择'No Warning Applicable/无需警示'选项")
                            time.sleep(1)
                        except Exception as e:
                            self.logger.error(f"选择选项失败: {str(e)}")
                            raise

                        # 滚动到form表单顶部
                        self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", form)
                        self.logger.info("已将form表单滚动到顶部")
                        time.sleep(2)
                    except Exception as e:
                        self.logger.error(f"操作输入框失败: {str(e)}")
                        raise

                except Exception as e:
                    self.logger.error(f"操作失败: {str(e)}")
                    raise
                
            except Exception as e:
                self.logger.error(f"选择待上传选项失败: {str(e)}")
                raise
            
        except Exception as e:
            self.logger.error(f"合规审核流程出错: {str(e)}")
            raise 