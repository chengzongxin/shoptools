import { Page, BrowserContext } from '@playwright/test';
import { logger } from '../utils/logger';

export class ComplianceReview {
    private page: Page;
    private debug: boolean;

    constructor(context: BrowserContext, debug: boolean = true) {
        this.page = context.pages()[0]; // 使用第一个页面
        this.debug = debug;
    }

    /**
     * 切换到新打开的标签页
     * @param timeout 等待超时时间（毫秒）
     * @returns 是否成功切换到新标签页
     */
    async switchToNewTab(timeout: number = 10000): Promise<boolean> {
        try {
            // 记录当前标签页数量
            const originalPages = this.page.context().pages();
            
            // 等待新标签页打开
            const startTime = Date.now();
            while (Date.now() - startTime < timeout) {
                const currentPages = this.page.context().pages();
                if (currentPages.length > originalPages.length) {
                    // 找到新打开的标签页
                    const newPage = currentPages[currentPages.length - 1];
                    this.page = newPage;
                    logger.info("已切换到新标签页");
                    return true;
                }
                await this.page.waitForTimeout(500);
            }
            
            logger.error("等待新标签页超时");
            return false;
        } catch (error) {
            logger.error(`切换到新标签页失败: ${error}`);
            return false;
        }
    }

    /**
     * 检查并关闭弹窗
     * @returns 是否发现并关闭了弹窗
     */
    async checkAndClosePopup(): Promise<boolean> {
        try {
            // 检查是否存在弹窗标题
            const popupTitle = await this.page.$('.PP_popoverTitle_5-114-0');
            
            if (popupTitle) {
                if (this.debug) {
                    console.log("发现弹窗，准备关闭...");
                }
                
                // 点击关闭按钮
                const closeButton = await this.page.waitForSelector('.new-bell_container__eWEgQ', { state: 'visible' });
                await closeButton?.click();
                
                // 等待弹窗消失
                await this.page.waitForTimeout(1000);
                
                if (this.debug) {
                    console.log("弹窗已关闭");
                }
                
                return true;
            }
            
            return false;
        } catch (error) {
            console.log(`检查或关闭弹窗失败: ${error}`);
            return false;
        }
    }

    /**
     * 点击合规待确认按钮
     */
    async clickCompliancePendingButton(): Promise<boolean> {
        try {
            // 首先检查并关闭可能存在的弹窗
            await this.checkAndClosePopup();

            if (this.debug) {
                console.log("正在查找合规待确认按钮...");
            }

            // 使用CSS选择器定位按钮
            const button = await this.page.waitForSelector(
                '#root > div > div > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)',
                { state: 'visible' }
            );
            
            if (!button) {
                throw new Error("未找到合规待确认按钮");
            }

            // 获取按钮文本（包含商品数量）
            const buttonText = await button.textContent();
            if (this.debug) {
                console.log(`找到合规待确认按钮: ${buttonText}`);
            }

            // 点击按钮
            await button.click();
            
            if (this.debug) {
                console.log("成功点击合规待确认按钮");
            }
            
            return true;
        } catch (error) {
            console.log(`点击合规待确认按钮失败: ${error}`);
            return false;
        }
    }

    /**
     * 滚动元素到视图
     * @param selector 元素选择器
     */
    private async scrollIntoView(selector: string): Promise<void> {
        await this.page.evaluate((sel) => {
            const element = document.querySelector(sel);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, selector);
        await this.page.waitForTimeout(1000);
    }

    /**
     * 滚动到drawer body底部
     */
    private async scrollDrawerBodyToBottom(): Promise<void> {
        try {
            const drawerBody = await this.page.$('.rocket-drawer-body');
            if (drawerBody) {
                await this.page.evaluate((element) => {
                    const viewportHeight = window.innerHeight;
                    const elementTop = element.getBoundingClientRect().top;
                    const elementBottom = element.getBoundingClientRect().bottom;
                    const scrollAmount = elementBottom - viewportHeight;
                    window.scrollBy(0, scrollAmount);
                }, drawerBody);
                logger.info("已将drawer body滚动到底部");
                await this.page.waitForTimeout(2000);
            }
        } catch (error) {
            logger.error(`滚动drawer body失败: ${error}`);
            throw error;
        }
    }

    /**
     * 开始合规审核流程
     */
    async startReview(): Promise<void> {
        try {
            logger.info("开始合规审核流程");
            
            // 1. 打开首页
            logger.info("正在打开首页...");
            await this.page.goto("https://seller.kuajingmaihuo.com/main/product/seller-select");
            await this.page.waitForTimeout(3000);
            
            // 2. 点击合规中心链接
            logger.info("正在查找合规中心链接...");
            const complianceLink = await this.page.waitForSelector(
                "a[data-report-click-text='合规中心']",
                { state: 'visible' }
            );
            await complianceLink?.click();
            logger.info("已点击合规中心链接");
            
            // 3. 处理授权弹窗
            logger.info("正在处理授权弹窗...");
            const authButton = await this.page.waitForSelector(
                "button.BTN_outerWrapper_5-114-0.BTN_primary_5-114-0.BTN_large_5-114-0.BTN_outerWrapperBtn_5-114-0",
                { state: 'visible' }
            );
            await authButton?.click();
            logger.info("已点击授权确认按钮");
            
            // 4. 切换到新标签页
            if (!await this.switchToNewTab()) {
                throw new Error("无法切换到新标签页");
            }
            
            // 5. 等待新页面加载完成
            logger.info("等待新页面加载...");
            await this.page.waitForTimeout(3000);
            
            // 6. 查找并点击商品合规信息菜单
            logger.info("正在查找商品合规信息菜单...");
            const menuItem = await this.page.waitForSelector(
                "//ul[contains(@class, 'rocket-menu') and contains(@class, 'rocket-menu-dark') and contains(@class, 'rocket-menu-root') and contains(@class, 'rocket-menu-inline')]//li[@title='商品合规信息']",
                { state: 'visible' }
            );
            await menuItem?.click();
            logger.info("已点击商品合规信息菜单");
            
            // 7. 等待页面加载并点击批量上传按钮
            logger.info("等待页面加载...");
            await this.page.waitForTimeout(3000);
            
            logger.info("正在查找批量上传按钮...");
            const uploadButton = await this.page.waitForSelector(
                "//*[@id='agentseller-layout-content']/div/div/div/button[1]",
                { state: 'visible' }
            );
            await uploadButton?.click();
            logger.info("已点击批量上传按钮");
            
            // 等待侧边栏出现
            await this.page.waitForTimeout(3000);
            
            // 等待并获取侧边栏表单
            logger.info("等待侧边栏表单加载...");
            // const form = await this.page.waitForSelector(
            //     ".rocket-drawer-content-wrapper form.rocket-form-field",
            //     { state: 'visible', timeout: 10000 }
            // );
            const form = this.page.locator(".rocket-drawer-content-wrapper form.rocket-form-field");
            await form.waitFor({ state: 'visible', timeout: 3000 });
            
            if (!form) {
                throw new Error("未找到侧边栏表单");
            }

            // 8. 选择合规信息类型
            logger.info("正在查找合规信息类型输入框...");
            try {
                // 定位到合规信息类型的选择器
                const selectElement = await this.page.waitForSelector(
                    ".rocket-drawer-content-wrapper .rocket-select-selector",
                    { state: 'visible' }
                );
                
                if (!selectElement) {
                    throw new Error("未找到合规信息类型选择器");
                }

                // 点击选择器
                await selectElement.click();
                logger.info("已点击合规信息类型选择器");
                
                // 等待下拉框出现
                await this.page.waitForTimeout(2000);

                // 检查下拉框是否出现
                const dropdown = await this.page.waitForSelector(
                    ".rocket-select-dropdown",
                    { timeout: 5000 }
                );
                
                if (!dropdown) {
                    throw new Error("点击后未出现下拉选项");
                }
                logger.info("下拉选项已出现");

            } catch (error) {
                logger.error(`点击合规信息类型输入框失败: ${error}`);
                throw error;
            }

            // 9. 选择"加利福尼亚州65号法案"选项
            logger.info("正在选择合规信息类型...");
            const option = await this.page.waitForSelector(
                "//div[contains(@class, 'rocket-select-item-option-content') and contains(text(), '加利福尼亚州65号法案')]",
                { state: 'visible' }
            );
            await option?.click();
            logger.info("已选择加利福尼亚州65号法案");

            // 等待页面刷新和筛选条件加载
            await this.page.waitForTimeout(3000);

            // 10. 选择状态筛选条件
            logger.info("正在选择状态筛选条件...");
            try {
                // 定位状态选择框 - 使用locator方法支持XPath
                const statusSelectLocator = form.locator(
                    'xpath=.//div[4]/div[3]/div/div[2]/div/div/div'
                  );
                
                // 等待元素可见
                await statusSelectLocator.waitFor({ state: 'visible', timeout: 5000 });
                
                // 点击状态选择框
                await statusSelectLocator.click();
                logger.info("已点击状态选择框");
                await this.page.waitForTimeout(1000);

                // 选择"待上传"选项
                const pendingOption = await this.page.waitForSelector(
                    "//div[contains(@class, 'rocket-select-item-option-content') and contains(text(), '待上传')]",
                    { state: 'visible', timeout: 5000 }
                );
                await pendingOption?.click();
                logger.info("已选择'待上传'选项");

                // 等待下拉菜单关闭
                await this.page.waitForTimeout(1000);

                // 使用ESC键关闭下拉菜单
                await this.page.keyboard.press('Escape');
                logger.info("已按ESC键关闭下拉菜单");

                // 等待下拉菜单完全关闭
                await this.page.waitForTimeout(1000);

                // 点击查询按钮
                logger.info("正在点击查询按钮...");
                await this.page.locator('.rocket-row').getByRole('button', { name: '查 询' }).first().click();
                logger.info("已点击查询按钮");

                // 等待页面刷新
                await this.page.waitForTimeout(3000);

                // 滚动表单到底部
                logger.info("正在滚动表单到底部...");
                await this.page.evaluate(() => {
                    const body = document.querySelector('.rocket-drawer-body');
                    if (body) {
                        body.scrollTo({
                            top: body.scrollHeight,
                            behavior: 'smooth'
                        });
                    }
                });
                logger.info("已滚动表单到底部");

                // 11. 选择商品
                logger.info("正在选择商品...");
                
                // 先选择每页显示100条
                logger.info("正在设置每页显示100条记录...");
                const pageSizeSelector = form.locator('.rocket-pagination-options .rocket-select-selector');
                
                // 等待并点击页码选择器
                await pageSizeSelector.waitFor({ state: 'visible', timeout: 5000 });
                await pageSizeSelector.click();
                logger.info("已点击页码选择器");
                
                // 等待下拉菜单出现并选择100条
                logger.info("正在查找100条/页选项...");
                
                // 等待下拉菜单出现
                await this.page.waitForSelector(
                    "div.rocket-select-dropdown",
                    { state: 'visible', timeout: 5000 }
                );
                
                // 使用更精确的选择器
                const pageSizeOption = await this.page.waitForSelector(
                    "div.rocket-select-item-option-content >> text='10 条/页'",
                    { state: 'visible', timeout: 5000 }
                );
                
                if (!pageSizeOption) {
                    throw new Error("未找到'10 条/页'选项");
                }
                
                await pageSizeOption.click();
                logger.info("已选择每页显示100条记录");
                
                // 等待页面刷新
                await this.page.waitForTimeout(2000);

                // 等待商品列表加载完成
                await this.page.waitForSelector('.rocket-table-content', { state: 'visible', timeout: 5000 });
                
                // 选择第一个商品
                const firstProductCheckbox = await this.page.waitForSelector(
                    '.rocket-table-selection-column .rocket-checkbox-input',
                    { state: 'visible', timeout: 5000 }
                );
                await firstProductCheckbox?.click();
                logger.info("已选择第一个商品");

                // 12. 选择警示类型
                logger.info("正在选择警示类型...");
                try {
                    // 定位警示类型选择框 - 使用更精确的选择器
                    const warningTypeLocator = form.locator(
                        "xpath=.//div[8]/div/div/div/div/div[2]/div[1]/div/div"
                    );

                    // 等待元素可见
                    await warningTypeLocator.waitFor({ state: 'visible', timeout: 5000 });
                    
                    // 点击警示类型选择框
                    await warningTypeLocator.click();
                    logger.info("已点击警示类型选择框");
                    await this.page.waitForTimeout(1000);

                    // 等待下拉列表出现
                    // const dropdownList = await this.page.waitForSelector(
                    //     "div.rocket-virtual-list-holder-inner",
                    //     { state: 'visible', timeout: 5000 }
                    // );

                    // dropdownList  = /html/body/div[17]/div/div
                    const dropdownList = await this.page.locator(
                        "xpath=.//div[17]/div/div"
                    );
                    logger.info(dropdownList)

                    // 选择"No Warning Applicable/无需警示"选项
                    const warningOption = await this.page.waitForSelector(
                        "div.rocket-select-item-option-content:has-text('No Warning Applicable/无需警示')",
                        { state: 'visible', timeout: 5000 }
                    );
                    await warningOption?.click();
                    logger.info("已选择'No Warning Applicable/无需警示'选项");

                    // 13. 确认协议
                    logger.info("正在确认协议...");
                    const policyCheckbox = await this.page.waitForSelector(
                        '#_policyApprove',
                        { state: 'visible', timeout: 5000 }
                    );
                    
                    if (!policyCheckbox) {
                        throw new Error("未找到协议确认复选框");
                    }

                    // 确保复选框被选中
                    const isChecked = await policyCheckbox.isChecked();
                    if (!isChecked) {
                        await policyCheckbox.click();
                    }
                    logger.info("已确认协议");

                    // 滚动表单到顶部
                    logger.info("正在滚动表单到顶部...");
                    await this.page.evaluate(() => {
                        const body = document.querySelector('.rocket-drawer-body');
                        if (body) {
                            body.scrollTo({
                                top: 0,
                                behavior: 'smooth'
                            });
                        }
                    });
                    logger.info("已滚动表单到顶部");

                    // 14. 点击确认上传按钮
                    logger.info("正在点击确认上传按钮...");
                    const confirmButton = await this.page.getByRole('button', { name: '确认上传' })
                    logger.info(confirmButton)
                    await confirmButton.click();
                    logger.info("已点击确认上传按钮");

                    // 等待上传完成
                    await this.page.waitForTimeout(3000);

                    // 15. 处理上传成功弹窗
                    logger.info("等待上传成功弹窗...");
                    const successButton = await this.page.waitForSelector(
                        "button.rocket-btn.rocket-btn-primary:has-text('我知道了')",
                        { state: 'visible', timeout: 5000 }
                    );
                    await successButton?.click();
                    logger.info("已关闭上传成功弹窗");

                    // 16. 检查是否有下一页并循环处理
                    while (true) {
                        // 检查是否存在"暂无数据"提示
                        const emptyDataElement = await this.page.locator('p.rocket-empty-description').first();
                        const isEmpty = await emptyDataElement.isVisible();
                        if (isEmpty) {
                            logger.info("检测到'暂无数据'提示，列表处理完成");
                            break;
                        }

                        // 获取当前页面的所有商品
                        await this.page.waitForSelector('.rocket-table-content', { state: 'visible', timeout: 5000 });

                        // 选择第一个商品
                        const firstProductCheckbox = await this.page.waitForSelector(
                            '.rocket-table-selection-column .rocket-checkbox-input',
                            { state: 'visible', timeout: 5000 }
                        );
                        await firstProductCheckbox?.click();
                        logger.info("已选择第一个商品");

                        // 点击确认上传按钮
                        logger.info("正在点击确认上传按钮...");
                        const confirmButton = await this.page.getByRole('button', { name: '确认上传' })
                        await confirmButton?.click();
                        logger.info("已点击确认上传按钮");

                        // 等待上传完成
                        await this.page.waitForTimeout(3000);

                        // 处理上传成功弹窗
                        logger.info("等待上传成功弹窗...");
                        const successButton = await this.page.waitForSelector(
                            "button.rocket-btn.rocket-btn-primary:has-text('我知道了')",
                            { state: 'visible', timeout: 5000 }
                        );
                        await successButton?.click();
                        logger.info("已关闭上传成功弹窗");
                    }

                } catch (error) {
                    logger.error(`选择警示类型或确认协议失败: ${error}`);
                    throw error;
                }

            } catch (error) {
                logger.error(`选择状态或商品失败: ${error}`);
                throw error;
            }

        } catch (error) {
            logger.error(`合规审核流程出错: ${error}`);
            throw error;
        }
    }
} 