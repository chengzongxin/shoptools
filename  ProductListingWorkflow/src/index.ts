import { chromium } from '@playwright/test';
import { logger } from './utils/logger';
import { BrowserManager } from './core/browser';
import { ComplianceReview } from './services/compliance';
import { PriceReview } from './services/price-review';

async function main() {
    const browserManager = new BrowserManager();
    
    try {
        logger.info('Temu卖家自动化工具启动');
        
        // 连接到已存在的浏览器
        await browserManager.connect(9222);
        
        // 获取浏览器上下文
        const context = browserManager.getContext();
        
        // 初始化价格审核
        const priceReview = new PriceReview(context);
        await priceReview.startReview();
        
        // 初始化合规审核
        const complianceReview = new ComplianceReview(context);
        await complianceReview.processAllComplianceTypes();
        
        // 等待用户手动关闭浏览器
        await new Promise(() => {});
        
    } catch (error) {
        logger.error(`执行过程中发生错误: ${error}`);
    }
}

main(); 