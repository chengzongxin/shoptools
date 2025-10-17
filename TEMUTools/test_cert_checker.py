"""
测试资质排查功能
"""
import logging
from src.modules.cert_checker.crawler import CertChecker

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_get_cert_types():
    """测试获取资质类型"""
    print("\n" + "="*60)
    print("测试1: 获取所有资质类型（排除GCC）")
    print("="*60)
    
    crawler = CertChecker(logger=logger)
    cert_types = crawler.get_all_cert_types()
    
    print(f"\n获取到 {len(cert_types)} 个资质类型")
    
    # 检查是否排除了GCC (id=28)
    gcc_found = any(cert.id == 28 for cert in cert_types)
    if gcc_found:
        print("❌ 错误: GCC资质(ID=28)未被排除!")
    else:
        print("✓ GCC资质(ID=28)已成功排除")
    
    # 显示前10个资质类型
    print("\n前10个资质类型:")
    for i, cert in enumerate(cert_types[:10], 1):
        print(f"  {i}. ID: {cert.id}, Name: {cert.name}")
    
    if len(cert_types) > 10:
        print(f"  ... 还有 {len(cert_types) - 10} 个资质类型")
    
    return cert_types

def test_query_products():
    """测试查询需要资质的商品"""
    print("\n" + "="*60)
    print("测试2: 查询需要资质的商品（使用前5个资质类型）")
    print("="*60)
    
    crawler = CertChecker(logger=logger)
    
    # 先获取资质类型
    cert_types = crawler.get_all_cert_types()
    if not cert_types:
        print("❌ 无法获取资质类型，测试终止")
        return []
    
    # 使用前5个资质类型进行测试
    test_cert_ids = [cert.id for cert in cert_types[:5]]
    print(f"\n使用资质类型ID: {test_cert_ids}")
    
    # 查询商品
    products = crawler.get_products_by_cert_types(test_cert_ids)
    
    print(f"\n找到 {len(products)} 个需要资质的商品")
    
    # 显示前5个商品
    if products:
        print("\n前5个商品（含库存信息）:")
        for i, product in enumerate(products[:5], 1):
            print(f"  {i}. ID: {product.productId}, Name: {product.productName}")
            print(f"     需要的资质类型: {product.requireCertTypes}")
            # 显示库存信息
            if product.productSkuSummaries:
                print(f"     SKU库存信息:")
                for sku in product.productSkuSummaries[:3]:  # 只显示前3个SKU
                    sku_id = sku.get('productSkuId', 'N/A')
                    stock = sku.get('virtualStock', 0)
                    print(f"       - SKU ID: {sku_id}, 虚拟库存: {stock}")
    
    return products

def test_batch_query():
    """测试分批查询所有资质商品"""
    print("\n" + "="*60)
    print("测试3: 分批查询所有资质商品（完整流程）")
    print("="*60)
    
    crawler = CertChecker(logger=logger)
    
    # 获取所有需要资质的商品
    products = crawler.get_all_cert_products()
    
    print(f"\n最终结果: 共找到 {len(products)} 个唯一的需要资质的商品")
    
    # 统计每个资质类型的商品数量
    cert_type_count = {}
    for product in products:
        for cert_id in product.requireCertTypes:
            cert_type_count[cert_id] = cert_type_count.get(cert_id, 0) + 1
    
    print(f"\n资质类型分布（前10个）:")
    sorted_certs = sorted(cert_type_count.items(), key=lambda x: x[1], reverse=True)
    for i, (cert_id, count) in enumerate(sorted_certs[:10], 1):
        print(f"  {i}. 资质ID {cert_id}: {count} 个商品")
    
    return products

if __name__ == "__main__":
    try:
        # 测试1: 获取资质类型
        cert_types = test_get_cert_types()
        
        if cert_types:
            # 测试2: 查询商品（使用部分资质类型）
            products = test_query_products()
            
            # 测试3: 完整的分批查询（可选，会花费较长时间）
            # 注意: 这会查询所有资质类型，可能需要几分钟
            user_input = input("\n是否执行完整的分批查询测试？(y/n): ").strip().lower()
            if user_input == 'y':
                all_products = test_batch_query()
                
                # 询问是否执行下架操作
                if all_products:
                    user_input = input(f"\n找到 {len(all_products)} 个商品，是否执行下架操作（设置库存为0）？(y/n): ").strip().lower()
                    if user_input == 'y':
                        print("\n" + "="*60)
                        print("执行下架操作")
                        print("="*60)
                        result = crawler.batch_set_stock_to_zero(max_workers=3)
                        print(f"\n下架完成:")
                        print(f"  成功: {result['success']} 个")
                        print(f"  失败: {result['failed']} 个")
                        print(f"  总计: {result['total']} 个")
            
        print("\n" + "="*60)
        print("所有测试完成！")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

