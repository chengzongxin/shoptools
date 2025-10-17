# 资质排查功能 - API 说明

## 库存设置接口说明

### API 地址
```
POST https://agentseller.temu.com/darwin-mms/api/kiana/foredawn/sales/stock/updateMmsSkuSalesStock
```

### 关键参数说明

#### `virtualStockDiff` - 虚拟库存变化量

⚠️ **重要**: `virtualStockDiff` 是**库存变化量**（差值），不是直接设置的库存值。

### 正确的使用方式

#### 将库存设为 0（下架商品）

1. **获取当前库存**: 从 `productSkuSummaries` 中读取 `virtualStock` 字段
2. **计算变化量**: 传入负数来减少库存
3. **发送请求**: `virtualStockDiff = -当前库存`

**示例**:
```json
{
  "productId": 5526152599,
  "productSkcId": 52759455592,
  "skuVirtualStockChangeList": [
    {
      "productSkuId": 80309695711,
      "virtualStockDiff": -20  // 当前库存是20，传入-20将库存减为0
    }
  ]
}
```

#### 增加库存

要增加库存，传入正数：
```json
{
  "virtualStockDiff": 1000  // 增加1000个库存
}
```

### 代码实现示例

```python
def set_product_stock_to_zero(self, product: CertProduct) -> Dict:
    """将商品库存设为0"""
    sku_list = []
    
    for sku in product.productSkuSummaries:
        # 1. 获取当前虚拟库存
        current_stock = sku.get("virtualStock", 0)
        
        # 2. 如果当前库存大于0，则传入负数减少到0
        if current_stock > 0:
            sku_list.append({
                "productSkuId": sku["productSkuId"],
                "virtualStockDiff": -current_stock  # 传入负数
            })
    
    # 3. 发送请求
    data = {
        "productId": product.productId,
        "productSkcId": product.productSkcId,
        "skuVirtualStockChangeList": sku_list
    }
    
    result = self.request.post(self.update_stock_url, data=data)
    return result
```

### 数据流程

```
1. 查询商品 → 获取 productSkuSummaries
   ↓
2. 读取每个 SKU 的 virtualStock（当前库存）
   ↓
3. 计算 virtualStockDiff = -virtualStock
   ↓
4. 发送请求更新库存
   ↓
5. 库存变为 0（商品下架）
```

## 相关API

### 1. 查询资质类型
```
GET https://agentseller.temu.com/visage-agent-seller/product/skc/certTypeEnum
```

返回所有资质类型列表，包含 `id` 和 `name`。

### 2. 查询需要资质的商品
```
POST https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery
```

请求参数:
```json
{
  "requireCertTypes": [29, 30, 31, ...],  // 最多500个资质ID
  "page": 1,
  "pageSize": 500
}
```

返回包含 `productSkuSummaries` 的商品列表，其中包含每个 SKU 的 `virtualStock`。

## 注意事项

1. ✅ GCC 资质（ID=28）会被自动排除
2. ✅ 如果资质类型超过500个，会自动分批查询
3. ✅ 同一商品可能触发多个资质，会自动去重
4. ✅ 只对库存大于0的商品进行下架操作
5. ✅ 支持多线程并发处理，提高效率

