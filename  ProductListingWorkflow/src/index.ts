import { chromium } from '@playwright/test';
import { logger } from './utils/logger';
import { BrowserManager } from './core/browser';
import { ComplianceReview } from './services/compliance';
import { PriceReview } from './services/price-review';

// 定义命令行参数接口
interface CommandOptions {
    port?: number;
    mode?: 'price' | 'compliance' | 'all';
    help?: boolean;
    version?: boolean;
}

// 解析命令行参数
function parseArgs(): CommandOptions {
    const args = process.argv.slice(2);
    const options: CommandOptions = {
        port: 9222,
        mode: 'all'
    };

    for (const arg of args) {
        if (arg.startsWith('--port=')) {
            options.port = parseInt(arg.split('=')[1]);
        } else if (arg === '--price') {
            options.mode = 'price';
        } else if (arg === '--compliance') {
            options.mode = 'compliance';
        } else if (arg === '--help' || arg === '-h') {
            options.help = true;
        } else if (arg === '--version' || arg === '-v') {
            options.version = true;
        }
    }

    return options;
}

// 显示帮助信息
function showHelp() {
    console.log(`
Temu卖家自动化工具

使用方法:
  npm start [选项]

选项:
  --port=<端口号>    指定浏览器调试端口 (默认: 9222)
  --price           仅运行价格审核
  --compliance      仅运行合规审核
  --help, -h        显示帮助信息
  --version, -v     显示版本信息

示例:
  npm start --price              # 仅运行价格审核
  npm start --compliance         # 仅运行合规审核
  npm start --port=9223         # 使用指定端口运行所有功能
    `);
}

// 显示版本信息
function showVersion() {
    console.log('版本: 1.0.0');
}

async function main() {
    const options = parseArgs();

    // 处理帮助和版本信息
    if (options.help) {
        showHelp();
        return;
    }
    if (options.version) {
        showVersion();
        return;
    }

    const browserManager = new BrowserManager();
    
    try {
        logger.info('Temu卖家自动化工具启动');
        logger.info(`运行模式: ${options.mode}`);
        logger.info(`使用端口: ${options.port}`);
        
        // 连接到已存在的浏览器
        await browserManager.connect(options.port || 9222);
        
        // 获取浏览器上下文
        const context = browserManager.getContext();
        
        // 根据模式执行不同的功能
        if (options.mode === 'price' || options.mode === 'all') {
            logger.info('开始价格审核...');
            const priceReview = new PriceReview(context);
            await priceReview.startReview();
        }
        
        if (options.mode === 'compliance' || options.mode === 'all') {
            logger.info('开始合规审核...');
            const complianceReview = new ComplianceReview(context);
            await complianceReview.processAllComplianceTypes();
        }
        
        // 等待用户手动关闭浏览器
        await new Promise(() => {});
        
    } catch (error) {
        logger.error(`执行过程中发生错误: ${error}`);
        process.exit(1);
    }
}

main(); 