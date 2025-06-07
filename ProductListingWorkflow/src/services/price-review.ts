import { Page, BrowserContext } from '@playwright/test';
import { logger } from '../utils/logger';
import { PriceMapper } from './price-mapper';
import * as fs from 'fs';
import * as path from 'path';

export class PriceReview {
    private page: Page;
    private priceMapper: PriceMapper;
    private logDir: string;
    private logFile: string;

    constructor(context: BrowserContext, debug: boolean = true) {
        this.page = context.pages()[0];
        this.priceMapper = new PriceMapper(debug);
        
        // 创建日志目录
        this.logDir = "logs";
        if (!fs.existsSync(this.logDir)) {
            fs.mkdirSync(this.logDir);
        }
        
        // 创建日志文件（使用日期作为文件名）
        const date = new Date().toISOString().split('T')[0].replace(/-/g, '');
        this.logFile = path.join(this.logDir, `price_review_${date}.log`);
        
        // 如果文件不存在，添加表头
        if (!fs.existsSync(this.logFile)) {
            fs.writeFileSync(this.logFile, 
                "=".repeat(80) + "\n" +
                `价格审核日志 - ${new Date().toLocaleDateString()}\n` +
                "=".repeat(80) + "\n\n",
                'utf-8'
            );
        }
    }

    /**
     * 记录价格审核日志
     */
    private logRecord(sku: string, spu: string, minPrice: number | string, newPrice: number | string, action: string): void {
        try {
            const timestamp = new Date().toLocaleString();
            const logEntry = `[${timestamp}] 货号: ${sku}, SPU: ${spu}, 最低核价: ${minPrice}, 新申报价格: ${newPrice}, 操作: ${action}\n`;
            
            fs.appendFileSync(this.logFile, logEntry, 'utf-8');
            
            logger.info(`已记录日志: ${logEntry.trim()}`);
        } catch (error) {
            logger.error(`记录日志失败: ${error}`);
        }
    }

    /**
     * 打开价格审核页面
     */
    private async openPriceReviewPage(): Promise<void> {
        try {
            logger.info("正在打开上新主页面...");
            await this.page.goto("https://seller.kuajingmaihuo.com/main/product/seller-select?topTab=0&quickTab=1");
            await this.page.waitForTimeout(3000);
            logger.info("页面加载完成");
        } catch (error) {
            logger.error(`打开价格审核页面失败: ${error}`);
            throw error;
        }
    }

    /**
     * 检查并关闭弹窗
     */
    private async checkAndClosePopup(): Promise<boolean> {
        try {
            const popupTitle = await this.page.$('.PP_popoverTitle_5-114-0');
            
            if (popupTitle) {
                logger.info("发现弹窗，准备关闭...");
                
                const closeButton = await this.page.waitForSelector('.new-bell_container__eWEgQ', { state: 'visible' });
                await closeButton?.click();
                
                await this.page.waitForTimeout(1000);
                
                logger.info("弹窗已关闭");
                return true;
            }
            
            return false;
        } catch (error) {
            logger.error(`检查或关闭弹窗失败: ${error}`);
            return false;
        }
    }

    /**
     * 设置每页显示10条记录
     */
    private async setPageSize(): Promise<boolean> {
        try {
            logger.info("正在设置每页显示数量...");

            const pageSizeInput = await this.page.waitForSelector(
                '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul/li[2]/div/div/div/div/div/div',
                { state: 'visible' }
            );
            await pageSizeInput?.click();
            
            // const option10 = await this.page.waitForSelector(
            //     '/html/body/div[6]/div/div/div/div/ul/li[1]',
            //     { state: 'visible' }
            // );
            // await option10?.click();

            const option10 = await this.page.waitForSelector(
                "li[role='option'] span:text('10')",
                { state: 'visible' }
            );
            await option10?.click();
            
            await this.page.waitForTimeout(2000);
            
            logger.info("已设置每页显示10条记录");
            return true;
        } catch (error) {
            logger.error(`设置每页显示数量失败: ${error}`);
            return false;
        }
    }

    /**
     * 点击价格待确认按钮
     */
    private async clickPricePendingButton(): Promise<boolean> {
        try {
            await this.checkAndClosePopup();
            await this.setPageSize();

            logger.info("正在查找价格待确认按钮...");

            const button = await this.page.waitForSelector(
                '#root > div > div > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(6)',
                { state: 'visible' }
            );
            
            const buttonText = await button?.textContent();
            logger.info(`找到价格待确认按钮: ${buttonText}`);

            await button?.click();
            logger.info("成功点击价格待确认按钮");
            
            return true;
        } catch (error) {
            logger.error(`点击价格待确认按钮失败: ${error}`);
            return false;
        }
    }

    /**
     * 获取分页信息
     */
    private async getPageInfo(): Promise<[number, number, number]> {
        try {
            const pagination = await this.page.waitForSelector(
                '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul',
                { state: 'visible' }
            );
            
            const totalItemsElement = await pagination?.$('./li[1]');
            const totalItemsText = await totalItemsElement?.textContent() || '';
            const totalItems = parseInt(totalItemsText.replace(/\D/g, ''));
            
            const currentPageElement = await this.page.waitForSelector(
                '.PGT_pagerItem_5-117-0.PGT_pagerItemActive_5-117-0',
                { state: 'visible' }
            );
            const currentPage = parseInt(await currentPageElement?.textContent() || '1');
            
            const totalPages = Math.ceil(totalItems / 10);
            
            logger.info(`分页信息: 总条数 ${totalItems}, 当前页 ${currentPage}/${totalPages}, 每页 10 条`);
            
            return [currentPage, totalPages, 10];
        } catch (error) {
            logger.error(`获取分页信息失败: ${error}`);
            return [1, 100, 10];
        }
    }

    /**
     * 跳转到下一页
     */
    private async goToNextPage(): Promise<boolean> {
        try {
            const pagination = await this.page.waitForSelector(
                '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul',
                { state: 'visible' }
            );
            
            try {
                const nextButton = await pagination?.$('.PGT_next_5-117-0');
                await nextButton?.click();
                logger.info("已跳转到下一页");
                return true;
            } catch (error) {
                logger.info("已到达最后一页，准备返回第一页");
                
                const firstPageButton = await this.page.waitForSelector(
                    '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul/li[4]',
                    { state: 'visible' }
                );
                await firstPageButton?.click();
                
                await this.page.waitForTimeout(2000);
                logger.info("已返回第一页");
                return true;
            }
        } catch (error) {
            logger.error(`页面跳转失败: ${error}`);
            return false;
        }
    }

    /**
     * 获取商品信息
     */
    private async getProductInfo(rowElement: any): Promise<{
        spu: string;
        sku: string;
        code: string | undefined;
        minPrice: number | undefined;
        priceButton: any;
    }> {
        try {
            const spuElement = await rowElement.$('div.product-info_name__pXkCK');
            const spuInfo = await spuElement?.textContent() || "未找到SPU信息";

            const skuElement = await rowElement.$('div.use-columns_infoItem__iPDoh.use-columns_light__sKFcQ');
            const skuNumber = await skuElement?.textContent() || "未找到货号";

            const priceButton = await rowElement.$('button.BTN_outerWrapper_5-111-0');
            
            const [code, minPrice] = this.priceMapper.getPriceInfo(skuNumber);
            
            logger.info(`\n商品信息:
SPU: ${spuInfo}
货号: ${skuNumber}
识别码: ${code}
最低核价: ${minPrice}
找到价格确认按钮: ${await priceButton?.textContent()}`);

            return {
                spu: spuInfo,
                sku: skuNumber,
                code,
                minPrice,
                priceButton
            };
        } catch (error) {
            logger.error(`获取商品信息失败: ${error}`);
            throw error;
        }
    }

    /**
     * 处理价格确认弹窗
     */
    private async handlePriceConfirmation(minPrice: number, sku: string, spu: string): Promise<boolean> {
        try {
            logger.info("\n开始处理价格确认弹窗...");

            const modal = await this.page.waitForSelector(".MDL_innerWrapper_5-111-0", { state: 'visible' });
            
            const priceElement = await this.page.waitForSelector(
                ".TB_whiteTr_5-111-0 td:nth-child(5) span:nth-child(2)",
                { state: 'visible' }
            );
            const newPrice = parseFloat(await priceElement?.textContent() || '0');
            
            logger.info(`最低核价: ${minPrice}`);
            logger.info(`新申报价格: ${newPrice}`);

            if (newPrice > minPrice) {
                logger.info("新申报价格大于最低核价，直接确认");
                
                const confirmButton = await this.page.waitForSelector(
                    ".MDL_okBtn_5-111-0",
                    { state: 'visible' }
                );

                await this.page.waitForTimeout(500);
                await confirmButton?.click();
                
                this.logRecord(sku, spu, minPrice, newPrice, "确认提交");
            } else {
                logger.info("新申报价格小于等于最低核价，选择放弃调整报价");
                
                const dropdown = await this.page.waitForSelector(
                    "#operatorType .ST_head_5-111-0",
                    { state: 'visible' }
                );
                await dropdown?.click();
                
                const abandonOption = await this.page.waitForSelector(
                    "li[role='option'] span:text('放弃调整报价')",
                    { state: 'visible' }
                );
                await abandonOption?.click();

                const confirmButton = await this.page.waitForSelector(
                    ".MDL_okBtn_5-111-0",
                    { state: 'visible' }
                );

                await this.page.waitForTimeout(500);
                await confirmButton?.click();
                
                this.logRecord(sku, spu, minPrice, newPrice, "放弃调整报价");
            }

            await this.page.waitForTimeout(2000);
            logger.info("价格确认处理完成");
            
            return true;
        } catch (error) {
            logger.error(`处理价格确认弹窗失败: ${error}`);
            this.logRecord(sku, spu, minPrice, "获取失败", `处理失败: ${error}`);
            return false;
        }
    }

    /**
     * 滚动到元素位置
     */
    private async scrollToElement(element: any): Promise<void> {
        try {
            await this.page.evaluate((el) => {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, element);
            await this.page.waitForTimeout(200);
        } catch (error) {
            logger.error(`滚动到元素位置失败: ${error}`);
        }
    }

    /**
     * 处理商品列表
     */
    private async processProductList(): Promise<void> {
        try {
            let currentPage = 1;
            while (true) {
                
                const productList = await this.page.waitForSelector(
                    '#root > div > div > div > div.TB_outerWrapper_5-117-0.TB_bordered_5-117-0.TB_notTreeStriped_5-117-0 > div.TB_inner_5-117-0 > div > div.TB_body_5-117-0 > div > div > table > tbody',
                    { state: 'visible' }
                );
                const rows = await productList?.$$('tr') || [];

                for (let index = 0; index < rows.length; index++) {
                    try {
                        logger.info(`\n处理第 ${index + 1} 个商品:`);
                        
                        await this.scrollToElement(rows[index]);
                        
                        const productInfo = await this.getProductInfo(rows[index]);
                        
                        await productInfo.priceButton?.click();
                        
                        if (productInfo.minPrice !== undefined) {
                            await this.handlePriceConfirmation(
                                productInfo.minPrice,
                                productInfo.sku,
                                productInfo.spu
                            );
                        }
                        
                        logger.info(`已处理第 ${index + 1} 个商品`);
                        
                        await this.page.waitForTimeout(2000);
                        
                    } catch (error) {
                        logger.error(`处理第 ${index + 1} 个商品时发生错误: ${error}`);
                        this.logRecord(
                            `第${index + 1}个商品`,
                            "获取失败",
                            "获取失败",
                            "获取失败",
                            `处理失败: ${error}`
                        );
                        continue;
                    }
                }

                const [currentPage, totalPages, itemsPerPage] = await this.getPageInfo();

                if (currentPage < totalPages) {
                    if (!await this.goToNextPage()) {
                        logger.info("无法跳转到下一页，处理结束");
                        break;
                    }
                    await this.page.waitForTimeout(2000);
                } else {
                    logger.info("已处理完所有页面，准备重新从第一页开始检查");
                    
                    const firstPageButton = await this.page.waitForSelector(
                        '//*[@id="root"]/div/div/div/div[3]/div[2]/div[2]/ul/li[4]',
                        { state: 'visible' }
                    );
                    await firstPageButton?.click();
                    
                    await this.page.waitForTimeout(2000);
                    
                    logger.info("已返回第一页，开始第二轮检查");
                    continue;
                }
            }
        } catch (error) {
            logger.error(`处理商品列表失败: ${error}`);
            throw error;
        }
    }

    /**
     * 开始价格审核流程
     */
    public async startReview(): Promise<void> {
        try {
            await this.openPriceReviewPage();
            // await this.clickPricePendingButton();
            // await this.page.waitForTimeout(3000);
            await this.setPageSize();
            await this.processProductList();
            logger.info("价格审核流程初始化完成");
        } catch (error) {
            logger.error(`价格审核流程初始化失败: ${error}`);
            throw error;
        }
    }
} 