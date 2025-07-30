# 要求：
首先获取商品列表，取出列表中所有productId和productSkcId，然后批量签署协议，20个一组，分批执行，直到所有产品都签署协议，然后再请求下一页，直到所有产品都签署协议

# 获取商品列表
https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery
## 请求参数 
{"page":1,"pageSize":200}
## 返回结构是这样的
{
    "success": true,
    "errorCode": 1000000,
    "errorMsg": null,
    "result": {
        "total": 31863,
        "pageItems": [
            {
                "productId": 2492963449,
                "productSkcId": 18882763424,
                "productName": "F 35 Lightning ilhouette  Drawstring Bags  lightweight closuresuitable for fitness outdoor sports travel  school and daily use",
                "productType": 1,
                "sourceType": 1,
                "goodsId": 601101786447529,
                "leafCat": {
                    "catId": 31563,
                    "catName": "抽绳健身包",
                    "catEnName": null,
                    "catType": 0
                },
                "sizeTemplateIds": null,
                "productTotalSalesVolume": 0,
                "extCode": "",
                "skcStatus": 1,
                "skcSiteStatus": 0,
                "mainImageUrl": "https://img.cdnfe.com/product/open/69050a9a02574e5f9947be521bc9e217-goods.jpeg",
                "last7DaysSalesVolume": null,
                "productSkuSummaries": [
                    {
                        "productSkuId": 10597160157,
                        "thumbUrl": "https://img.cdnfe.com/product/open/cb332a2e59994adba6d0c844d8f2cf0a-goods.jpeg",
                        "productSkuSpecList": [
                            {
                                "parentSpecId": 1001,
                                "parentSpecName": "颜色",
                                "specId": 19176,
                                "specName": "Multicolor",
                                "unitSpecName": null
                            },
                            {
                                "parentSpecId": 3001,
                                "parentSpecName": "尺码",
                                "specId": 49671929,
                                "specName": "单尺码",
                                "unitSpecName": null
                            }
                        ],
                        "currencyType": "CNY",
                        "financeExchangeRate": null,
                        "supplierPrice": 2200,
                        "supplierPriceUS": null,
                        "siteSupplierPrices": null,
                        "extCode": "drawing_#NPJESJZ",
                        "productSkuWhExtAttr": {
                            "productSkuVolume": {
                                "len": 130,
                                "width": 130,
                                "height": 20,
                                "inputLen": null,
                                "inputWidth": null,
                                "inputHeight": null,
                                "inputUnit": null
                            },
                            "productSkuWeight": {
                                "value": 92000,
                                "inputValue": null,
                                "inputUnit": null
                            },
                            "productSkuVolumeLabel": null,
                            "productSkuWmsVolume": null,
                            "productSkuWmsWeight": null,
                            "productSkuWmsVolumeLabel": null,
                            "productSkuBarCodes": null,
                            "productSkuSensitiveAttr": {
                                "isSensitive": 0,
                                "sensitiveTypes": [],
                                "sensitiveList": [],
                                "isForce2Normal": false,
                                "force2NormalTypes": null
                            },
                            "productSkuSensitiveLimit": {
                                "maxBatteryCapacity": null,
                                "maxLiquidCapacity": null,
                                "maxKnifeLength": null,
                                "maxBatteryCapacityHp": null,
                                "maxLiquidCapacityHp": null,
                                "maxKnifeLengthHp": null,
                                "knifeTipAngle": null
                            },
                            "productSkuFragileLabelAttr": null,
                            "latestShippingModeEditRecord": null,
                            "productSkuSameReference": null
                        },
                        "productSkuSaleExtAttr": {
                            "productSkuCustomizationTmpl": null,
                            "productSkuShippingMode": null,
                            "productSkuAccessories": null,
                            "productSkuIndividuallyPacked": null,
                            "productSkuNetContent": null,
                            "productSkuStockDisplayOption": null
                        },
                        "todaySalesVolume": null,
                        "realStock": null,
                        "virtualStock": null,
                        "virtualStockLimitType": null,
                        "salesStockLockType": null,
                        "stockLockDetailList": null,
                        "tempLockNum": null,
                        "productSkuSemiManagedStock": null,
                        "sampleNetWeight": null,
                        "productSkuCwVOList": null,
                        "productSkuMultiPack": {
                            "skuClassification": 1,
                            "numberOfPieces": 1,
                            "pieceUnitCode": 1,
                            "individuallyPacked": null,
                            "productSkuNetContent": null
                        },
                        "priceReviewStatus": null,
                        "flowLimit": null,
                        "preLimitTime": null
                    }
                ],
                "createdAt": 1750140352000,
                "productJitMode": {
                    "matchJitMode": false,
                    "quickSellAgtSignStatus": null,
                    "signLatestAgt": true
                },
                "productCertAuditStatus": null,
                "offSaleByNoCert": null,
                "noCertPunishRecord": null,
                "productCertConfig": null,
                "productCertPunish": null,
                "productPersonalization": {
                    "personalizationSwitch": null,
                    "personalizationTmp": null,
                    "signLatestAgt": false,
                    "personalizationAgtSignStatus": null
                },
                "goodsAdvantageLabelVOList": null,
                "productTags": null,
                "productFragileLabelAttr": {
                    "isFragile": false
                },
                "productGuideFileI18nList": [],
                "productGuideFileNewVOList": [],
                "printedGuideFileInfoVO": null,
                "productPropAdjustTasks": null,
                "needGuideFile": false,
                "productGuideFileIfNeed": null,
                "guideFileStatus": null,
                "guideFileFailReason": null,
                "electronicGuideFileComplianceLabel": 1,
                "printedGuideFileComplianceLabel": 1,
                "productSelected": false,
                "canEditSizeTemplate": null,
                "inProcessEditTasks": null,
                "productAuditDraft": null,
                "hasDecoration": null,
                "hasCarouseVideo": null,
                "hasDetailVideo": null,
                "matchSkcJitMode": false,
                "isJitUnSignForMms": false,
                "guideFileAttribute": null,
                "similarClusterProduct": null,
                "guideFilePageImages": null,
                "isSupportPersonalization": false,
                "supplierSourceType": 1000,
                "productSemiManaged": null,
                "productPublishLabel": null,
                "productPattern": {
                    "canRelatePattern": false,
                    "patternId": null,
                    "isModified": null,
                    "garmentPreviewPics": null,
                    "paperPreviewPics": null,
                    "patternFile": null,
                    "modifiedPaperPreviewPics": null,
                    "modifiedPatternFile": null
                },
                "productCustomizationTechnology": null,
                "hotSaleGoodsLabelStyle": null,
                "sensitiveAttrProblemTag": false,
                "classId": null,
                "industrySelectionTag": false,
                "allowanceCertList": null,
                "flowAllowanceSiteList": null,
                "flowAllowanceStatus": 1,
                "newProductCatMisplace": {
                    "matchMisplace": false,
                    "recCategoriesList": [],
                    "feedback": null
                },
                "productPotentialInfo": null,
                "hotSaleCarouselVideoNeedUpload": false,
                "highPrice": null
            }
                "productId": 5443512721,
                "productSkcId": 83527605037,
                "productName": "Immune Cell Color  Drawstring Bags  lightweight closuresuitable for fitness outdoor sports travel  school and daily use",
                "productType": 1,
                "sourceType": 1,
                "goodsId": 601101786084233,
                "leafCat": {
                    "catId": 31563,
                    "catName": "抽绳健身包",
                    "catEnName": null,
                    "catType": 0
                },
                "sizeTemplateIds": null,
                "productTotalSalesVolume": 0,
                "extCode": "",
                "skcStatus": 7,
                "skcSiteStatus": 0,
                "mainImageUrl": "https://img.cdnfe.com/product/open/1d219bda073f47bc8ece7cf80a138c38-goods.jpeg",
                "last7DaysSalesVolume": null,
                "productSkuSummaries": [
                    {
                        "productSkuId": 88834195244,
                        "thumbUrl": "https://img.cdnfe.com/product/open/5ea8056f05be4a7f8800c0bbdff0de0c-goods.jpeg",
                        "productSkuSpecList": [
                            {
                                "parentSpecId": 1001,
                                "parentSpecName": "颜色",
                                "specId": 19176,
                                "specName": "Multicolor",
                                "unitSpecName": null
                            },
                            {
                                "parentSpecId": 3001,
                                "parentSpecName": "尺码",
                                "specId": 49671929,
                                "specName": "单尺码",
                                "unitSpecName": null
                            }
                        ],
                        "currencyType": "CNY",
                        "financeExchangeRate": null,
                        "supplierPrice": 2200,
                        "supplierPriceUS": null,
                        "siteSupplierPrices": null,
                        "extCode": "drawing_#N3CRPNX",
                        "productSkuWhExtAttr": {
                            "productSkuVolume": {
                                "len": 130,
                                "width": 130,
                                "height": 20,
                                "inputLen": null,
                                "inputWidth": null,
                                "inputHeight": null,
                                "inputUnit": null
                            },
                            "productSkuWeight": {
                                "value": 92000,
                                "inputValue": null,
                                "inputUnit": null
                            },
                            "productSkuVolumeLabel": null,
                            "productSkuWmsVolume": null,
                            "productSkuWmsWeight": null,
                            "productSkuWmsVolumeLabel": null,
                            "productSkuBarCodes": null,
                            "productSkuSensitiveAttr": {
                                "isSensitive": 0,
                                "sensitiveTypes": [],
                                "sensitiveList": [],
                                "isForce2Normal": false,
                                "force2NormalTypes": null
                            },
                            "productSkuSensitiveLimit": {
                                "maxBatteryCapacity": null,
                                "maxLiquidCapacity": null,
                                "maxKnifeLength": null,
                                "maxBatteryCapacityHp": null,
                                "maxLiquidCapacityHp": null,
                                "maxKnifeLengthHp": null,
                                "knifeTipAngle": null
                            },
                            "productSkuFragileLabelAttr": null,
                            "latestShippingModeEditRecord": null,
                            "productSkuSameReference": null
                        },
                        "productSkuSaleExtAttr": {
                            "productSkuCustomizationTmpl": null,
                            "productSkuShippingMode": null,
                            "productSkuAccessories": null,
                            "productSkuIndividuallyPacked": null,
                            "productSkuNetContent": null,
                            "productSkuStockDisplayOption": null
                        },
                        "todaySalesVolume": null,
                        "realStock": null,
                        "virtualStock": 0,
                        "virtualStockLimitType": null,
                        "salesStockLockType": null,
                        "stockLockDetailList": null,
                        "tempLockNum": null,
                        "productSkuSemiManagedStock": null,
                        "sampleNetWeight": null,
                        "productSkuCwVOList": null,
                        "productSkuMultiPack": {
                            "skuClassification": 1,
                            "numberOfPieces": 1,
                            "pieceUnitCode": 1,
                            "individuallyPacked": null,
                            "productSkuNetContent": null
                        },
                        "priceReviewStatus": 1,
                        "flowLimit": null,
                        "preLimitTime": null
                    }
                ],
                "createdAt": 1750140349000,
                "productJitMode": {
                    "matchJitMode": true,
                    "quickSellAgtSignStatus": 1,
                    "signLatestAgt": true
                },
                "productCertAuditStatus": null,
                "offSaleByNoCert": null,
                "noCertPunishRecord": null,
                "productCertConfig": null,
                "productCertPunish": null,
                "productPersonalization": {
                    "personalizationSwitch": null,
                    "personalizationTmp": null,
                    "signLatestAgt": false,
                    "personalizationAgtSignStatus": null
                },
                "goodsAdvantageLabelVOList": null,
                "productTags": null,
                "productFragileLabelAttr": {
                    "isFragile": false
                },
                "productGuideFileI18nList": [],
                "productGuideFileNewVOList": [],
                "printedGuideFileInfoVO": null,
                "productPropAdjustTasks": null,
                "needGuideFile": false,
                "productGuideFileIfNeed": null,
                "guideFileStatus": null,
                "guideFileFailReason": null,
                "electronicGuideFileComplianceLabel": 1,
                "printedGuideFileComplianceLabel": 1,
                "productSelected": true,
                "canEditSizeTemplate": null,
                "inProcessEditTasks": null,
                "productAuditDraft": null,
                "hasDecoration": null,
                "hasCarouseVideo": null,
                "hasDetailVideo": null,
                "matchSkcJitMode": true,
                "isJitUnSignForMms": false,
                "guideFileAttribute": null,
                "similarClusterProduct": null,
                "guideFilePageImages": null,
                "isSupportPersonalization": false,
                "supplierSourceType": 1000,
                "productSemiManaged": null,
                "productPublishLabel": null,
                "productPattern": {
                    "canRelatePattern": false,
                    "patternId": null,
                    "isModified": null,
                    "garmentPreviewPics": null,
                    "paperPreviewPics": null,
                    "patternFile": null,
                    "modifiedPaperPreviewPics": null,
                    "modifiedPatternFile": null
                },
                "productCustomizationTechnology": null,
                "hotSaleGoodsLabelStyle": null,
                "sensitiveAttrProblemTag": false,
                "classId": null,
                "industrySelectionTag": false,
                "allowanceCertList": null,
                "flowAllowanceSiteList": null,
                "flowAllowanceStatus": 1,
                "newProductCatMisplace": {
                    "matchMisplace": false,
                    "recCategoriesList": [],
                    "feedback": null
                },
                "productPotentialInfo": null,
                "hotSaleCarouselVideoNeedUpload": false,
                "highPrice": null


    }
}




# 批量签署协议
## 请求
### 请求地址
https://agentseller.temu.com/visage-agent-seller/product/agreement/batch/sign
### 请求参数
{"skcList":[{"productId":2814039484,"productSkcId":24247148994},{"productId":9743874592,"productSkcId":67772594382},{"productId":5513338646,"productSkcId":91396794869},{"productId":8367939978,"productSkcId":89733512131},{"productId":2132346469,"productSkcId":84516410360},{"productId":9508685084,"productSkcId":20413575915},{"productId":7996867778,"productSkcId":78939106962},{"productId":7596746291,"productSkcId":79600281432},{"productId":7508749264,"productSkcId":34621979075},{"productId":2918004650,"productSkcId":42474207955},{"productId":5711151325,"productSkcId":94532226854},{"productId":1338372860,"productSkcId":46168329550},{"productId":2535068596,"productSkcId":79349424570},{"productId":7590767999,"productSkcId":46643836912},{"productId":8725920720,"productSkcId":99746444634},{"productId":3702333630,"productSkcId":96214489215},{"productId":1935430103,"productSkcId":27531567012},{"productId":3140333040,"productSkcId":71293098682},{"productId":1518842128,"productSkcId":35972087928},{"productId":3667065541,"productSkcId":38989542023}]}
### 返回结构
{
    "success": true,
    "errorCode": 1000000,
    "errorMsg": null,
    "result": {
        "successNum": 20,
        "failedNum": 0,
        "failedDetailList": null
    }
}










