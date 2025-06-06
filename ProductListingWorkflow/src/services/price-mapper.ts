import { logger } from '../utils/logger';

export class PriceMapper {
    private priceMapping: Record<string, number> = {
        "drawing": 12.7,
        "CB": 10.7,
        "SLEEVE": 11.4,
        "SH": 8.7,
        "Scarf": 7.4,
        "Sock": 10.7,
        "Apron": 10.0
    };

    constructor(private debug: boolean = true) {}

    /**
     * 清理货号，移除多余文字
     * @param sku 原始货号文本
     * @returns 清理后的货号
     */
    private cleanSku(sku: string): string {
        try {
            // 移除"货号："前缀
            if (sku.includes("货号：")) {
                sku = sku.replace("货号：", "");
            }
            
            // 移除"SPU："前缀
            if (sku.includes("SPU：")) {
                sku = sku.replace("SPU：", "");
            }
            
            // 移除多余空格
            sku = sku.trim();
            
            if (this.debug) {
                logger.info(`清理后的货号: ${sku}`);
            }
            
            return sku;
        } catch (error) {
            logger.error(`清理货号失败: ${error}`);
            return sku;
        }
    }

    /**
     * 从货号中获取价格
     * @param sku 货号
     * @returns 价格或undefined
     */
    private getMinPrice(sku: string): number | undefined {
        try {
            // 清理货号
            sku = this.cleanSku(sku);
            
            // 提取货号前缀（第一个下划线之前的部分）
            const prefix = sku.includes('_') ? sku.split('_')[0] : sku;
            
            // 获取价格
            const price = this.priceMapping[prefix];
            
            if (price === undefined) {
                if (this.debug) {
                    logger.info(`未找到货号 ${sku} 对应的价格`);
                }
                return undefined;
            }
            
            if (this.debug) {
                logger.info(`原始货号: ${sku}`);
                logger.info(`提取的前缀: ${prefix}`);
                logger.info(`对应价格: ${price}`);
            }
            
            return price;
        } catch (error) {
            logger.error(`获取价格失败: ${error}`);
            return undefined;
        }
    }

    /**
     * 获取货号对应的价格信息
     * @param sku 货号
     * @returns [货号前缀, 价格] 元组
     */
    public getPriceInfo(sku: string): [string | undefined, number | undefined] {
        try {
            // 清理货号
            sku = this.cleanSku(sku);
            
            // 提取货号前缀
            const prefix = sku.includes('_') ? sku.split('_')[0] : sku;
            
            // 获取价格
            const price = this.getMinPrice(sku);
            
            return [prefix, price];
        } catch (error) {
            logger.error(`获取价格信息失败: ${error}`);
            return [undefined, undefined];
        }
    }
} 