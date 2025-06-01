from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ViolationListExcelExporter:
    """违规商品列表Excel导出器"""
    
    def __init__(self):
        self.columns = [
            'SPUID', '商品ID', '商品名称', '违规类型', '违规描述', '处罚类型',
            '处罚描述', '违规详情', '整改建议', '处罚开始时间', '处罚结束时间',
            '申诉状态', '申诉次数', '最大申诉次数'
        ]
    
    def format_timestamp(self, timestamp: int) -> str:
        """格式化时间戳为可读时间"""
        if not timestamp:
            return ''
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return ''
    
    def format_appeal_status(self, status: int) -> str:
        """格式化申诉状态"""
        status_map = {
            0: '未申诉',
            1: '申诉中',
            2: '申诉通过',
            3: '申诉驳回'
        }
        return status_map.get(status, '未知状态')
    
    def export_to_excel(self, data: List[Dict[str, Any]], file_path: str) -> bool:
        """导出数据到Excel文件
        
        Args:
            data: 违规商品数据列表
            file_path: 导出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        try:
            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "违规商品列表"
            
            # 写入表头
            headers = [
                "SPUID", "商品名称", "违规原因", "违规描述",
                "处罚类型", "处罚影响", "违规详情", "整改建议",
                "开始时间", "结束时间", "申诉状态", "申诉次数", "最大申诉次数"
            ]
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            # 写入数据
            row = 2
            for product in data:
                # 获取第一个处罚详情（如果有的话）
                punish_detail = product.get('punish_detail_list', [{}])[0] if product.get('punish_detail_list') else {}
                
                # 获取违规详情
                illegal_details = punish_detail.get('illegal_detail', [])
                illegal_desc = '; '.join([
                    f"{illegal.get('title', '')}: {illegal.get('value', '')}"
                    for illegal in illegal_details
                ])
                
                # 格式化时间戳
                start_time = self.format_timestamp(punish_detail.get('start_time'))
                end_time = self.format_timestamp(punish_detail.get('plan_end_time'))
                
                # 写入一行数据
                ws.cell(row=row, column=1, value=product.get('spu_id', ''))
                ws.cell(row=row, column=2, value=product.get('goods_name', ''))
                ws.cell(row=row, column=3, value=product.get('leaf_reason_name', ''))
                ws.cell(row=row, column=4, value=product.get('violation_desc', ''))
                ws.cell(row=row, column=5, value=punish_detail.get('punish_appeal_type', ''))
                ws.cell(row=row, column=6, value=punish_detail.get('punish_infect_desc', ''))
                ws.cell(row=row, column=7, value=illegal_desc)
                ws.cell(row=row, column=8, value=punish_detail.get('rectification_suggestion', ''))
                ws.cell(row=row, column=9, value=start_time)
                ws.cell(row=row, column=10, value=end_time)
                ws.cell(row=row, column=11, value=self.format_appeal_status(punish_detail.get('appeal_status', 0)))
                ws.cell(row=row, column=12, value=punish_detail.get('now_appeal_time', 0))
                ws.cell(row=row, column=13, value=punish_detail.get('max_appeal_time', 0))
                
                row += 1
            
            # 调整列宽
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                ws.column_dimensions[column].width = adjusted_width
            
            # 保存文件
            wb.save(file_path)
            return True
            
        except Exception as e:
            logger.error(f"导出Excel时出错: {str(e)}")
            return False 