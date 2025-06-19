#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
违规列表功能测试脚本
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

from modules.violation_list.crawler import ViolationListCrawler

def test_violation_list_crawler():
    """测试违规列表爬虫"""
    print("开始测试违规列表爬虫...")
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('test_violation_list')
    
    try:
        # 创建爬虫实例
        crawler = ViolationListCrawler(logger=logger)
        
        # 测试获取第一页数据
        logger.info("测试获取第一页数据...")
        result = crawler.get_page_data(page=1, page_size=10)
        
        if result:
            logger.info("✅ 第一页数据获取成功")
            logger.info(f"响应结构: {list(result.keys())}")
            
            if 'result' in result:
                items = result['result'].get('punish_appeal_entrance_list', [])
                logger.info(f"获取到 {len(items)} 条违规商品数据")
                
                if items:
                    # 显示第一条数据的结构
                    first_item = items[0]
                    logger.info(f"第一条数据字段: {list(first_item.keys())}")
                    logger.info(f"商品名称: {first_item.get('goods_name', 'N/A')}")
                    logger.info(f"SPU ID: {first_item.get('spu_id', 'N/A')}")
                    logger.info(f"违规原因: {first_item.get('leaf_reason_name', 'N/A')}")
                else:
                    logger.warning("当前页面没有违规商品数据")
            else:
                logger.error("响应数据格式错误，缺少result字段")
        else:
            logger.error("❌ 第一页数据获取失败")
            return False
            
        # 测试获取多页数据
        logger.info("测试获取多页数据...")
        all_data = crawler.get_all_data(max_pages=1, page_size=10)
        
        if all_data:
            logger.info(f"✅ 成功获取 {len(all_data)} 条违规商品数据")
            
            # 显示第一条数据的详细信息
            if all_data:
                first_product = all_data[0]
                logger.info(f"第一条商品数据:")
                logger.info(f"  - 商品名称: {first_product.get('goods_name', 'N/A')}")
                logger.info(f"  - SPU ID: {first_product.get('spu_id', 'N/A')}")
                logger.info(f"  - 违规原因: {first_product.get('leaf_reason_name', 'N/A')}")
                logger.info(f"  - 违规描述: {first_product.get('violation_desc', 'N/A')}")
                
                # 检查处罚详情
                punish_details = first_product.get('punish_detail_list', [])
                logger.info(f"  - 处罚详情数量: {len(punish_details)}")
                
                if punish_details:
                    first_detail = punish_details[0]
                    logger.info(f"  - 处罚类型: {first_detail.get('punish_appeal_type', 'N/A')}")
                    logger.info(f"  - 处罚影响: {first_detail.get('punish_infect_desc', 'N/A')}")
                    logger.info(f"  - 申诉状态: {first_detail.get('appeal_status', 'N/A')}")
        else:
            logger.warning("未获取到任何违规商品数据")
            
        logger.info("✅ 违规列表爬虫测试完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("违规列表功能测试")
    print("=" * 50)
    
    success = test_violation_list_crawler()
    
    print("=" * 50)
    if success:
        print("✅ 测试通过")
    else:
        print("❌ 测试失败")
    print("=" * 50) 