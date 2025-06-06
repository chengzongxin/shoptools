import { chromium, Browser, BrowserContext } from '@playwright/test';
import { logger } from '../utils/logger';

export class BrowserManager {
    private browser: Browser | null = null;
    private context: BrowserContext | null = null;

    /**
     * 连接到已存在的浏览器
     * @param debugPort 调试端口号
     */
    async connect(debugPort: number = 9222): Promise<void> {
        try {
            logger.info(`正在连接到已存在的浏览器，调试端口: ${debugPort}`);
            
            // 连接到已存在的浏览器
            this.browser = await chromium.connectOverCDP(`http://localhost:${debugPort}`);
            
            // 获取默认上下文
            const contexts = this.browser.contexts();
            if (contexts.length > 0) {
                this.context = contexts[0];
            } else {
                this.context = await this.browser.newContext();
            }

            logger.info('成功连接到浏览器');
        } catch (error) {
            logger.error('连接浏览器失败:', error);
            throw error;
        }
    }

    /**
     * 启动新的浏览器实例
     * @param debugPort 调试端口号
     */
    async launch(debugPort: number = 9222): Promise<void> {
        try {
            logger.info(`正在启动浏览器，调试端口: ${debugPort}`);
            
            this.browser = await chromium.launch({
                headless: false, // 非无头模式
                args: [
                    `--remote-debugging-port=${debugPort}`,
                    '--start-maximized'
                ]
            });

            this.context = await this.browser.newContext({
                viewport: null, // 禁用视口大小限制
                userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            });

            logger.info('浏览器启动成功');
        } catch (error) {
            logger.error('浏览器启动失败:', error);
            throw error;
        }
    }

    /**
     * 获取浏览器上下文
     */
    getContext(): BrowserContext {
        if (!this.context) {
            throw new Error('浏览器上下文未初始化');
        }
        return this.context;
    }

    /**
     * 关闭浏览器
     */
    async close(): Promise<void> {
        try {
            if (this.context) {
                await this.context.close();
            }
            if (this.browser) {
                await this.browser.close();
            }
            logger.info('浏览器已关闭');
        } catch (error) {
            logger.error('关闭浏览器时出错:', error);
            throw error;
        }
    }
} 