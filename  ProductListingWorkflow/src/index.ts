import { logger } from './utils/logger';
import { BrowserManager } from './core/browser';
import { ComplianceReview } from './services/compliance';

async function main() {
    const browserManager = new BrowserManager();
    
    try {
        logger.info('Temu卖家自动化工具启动');
        
        // 连接到已存在的浏览器
        await browserManager.connect(9222);
        
        // 获取浏览器上下文
        const context = browserManager.getContext();
        
        // 创建合规审核实例
        const complianceReview = new ComplianceReview(context, true);
        
        // 开始合规审核流程
        await complianceReview.startReview();
        
        logger.info('合规审核流程完成，等待用户操作...');
        
        // 保持程序运行
        await new Promise(() => {});
        
    } catch (error) {
        logger.error('程序运行出错:', error);
    } finally {
        // 确保浏览器正确关闭
        await browserManager.close();
    }
}

main(); 