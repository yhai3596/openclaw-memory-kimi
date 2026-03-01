"""
数据导入模块
支持从 Zoho Desk 导出的 Excel 文件导入
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

class DataImporter:
    def __init__(self):
        self.required_columns = ['Ticket Id', 'Subject', 'Created Time (Ticket)']
        self.optional_columns = [
            'Ticket Description', 'Ticket Type', 
            'Condenser Model Number', 'Condenser Serial Number',
            'Air Handler/A Coil Model Number', 'Air Handler/ A Coil Serial Number',
            'Category (Ticket)'
        ]
    
    def validate_columns(self, df):
        """验证必要的列是否存在"""
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"缺少必要列: {missing}")
        return True
    
    def clean_text(self, text):
        """清理文本"""
        if pd.isna(text):
            return None
        text = str(text).strip()
        if text in ['-', 'nan', '']:
            return None
        return text
    
    def merge_fields(self, row):
        """合并 Subject + Description + Type"""
        parts = []
        
        # 1. Subject（主要描述）
        subject = self.clean_text(row.get('Subject'))
        if subject:
            parts.append(subject)
        
        # 2. Description（过滤系统模板）
        description = self.clean_text(row.get('Ticket Description'))
        if description:
            # 过滤 Zoho Voice 自动生成内容
            if not description.startswith('Hey\n\nYou have the following incoming call'):
                parts.append(description)
        
        # 3. Type（辅助）
        ticket_type = self.clean_text(row.get('Ticket Type'))
        if ticket_type:
            parts.append(f"Type: {ticket_type}")
        
        return ' | '.join(parts) if parts else None
    
    def parse_date(self, date_str):
        """解析日期字符串"""
        if pd.isna(date_str):
            return None
        
        formats = [
            '%d %b %Y %I:%M %p',      # 28 Oct 2024 04:26 AM
            '%Y-%m-%d %H:%M:%S',       # 2024-10-28 04:26:00
            '%m/%d/%Y %H:%M',          # 10/28/2024 04:26
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def import_excel(self, file_path, db):
        """导入 Excel 文件"""
        print(f"正在导入: {file_path}")
        
        # 读取 Excel
        df = pd.read_excel(file_path)
        print(f"读取到 {len(df)} 行数据")
        
        # 验证列
        self.validate_columns(df)
        
        # 处理每一行
        imported_count = 0
        for idx, row in df.iterrows():
            try:
                # 合并字段
                merged_text = self.merge_fields(row)
                if not merged_text:
                    print(f"跳过行 {idx}: 无有效文本")
                    continue
                
                # 构建数据
                data = {
                    'ticket_id': self.clean_text(row.get('Ticket Id')),
                    'subject': self.clean_text(row.get('Subject')),
                    'description': self.clean_text(row.get('Ticket Description')),
                    'ticket_type': self.clean_text(row.get('Ticket Type')),
                    'model': self.clean_text(row.get('Condenser Model Number')),
                    'model_serial': self.clean_text(row.get('Condenser Serial Number')),
                    'air_handler_model': self.clean_text(row.get('Air Handler/A Coil Model Number')),
                    'air_handler_serial': self.clean_text(row.get('Air Handler/ A Coil Serial Number')),
                    'region': None,  # 暂时未解析地区
                    'created_at': self.parse_date(row.get('Created Time (Ticket)')),
                    'merged_text': merged_text,
                    'category': self.clean_text(row.get('Category (Ticket)'))
                }
                
                # 插入数据库
                feedback_id = db.insert_feedback(data)
                imported_count += 1
                
            except Exception as e:
                print(f"处理行 {idx} 时出错: {e}")
                continue
        
        print(f"成功导入 {imported_count} 条记录")
        return imported_count
    
    def get_training_data(self, db):
        """获取用于训练的数据（已分类的）"""
        conn = db.conn if hasattr(db, 'conn') else sqlite3.connect(db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.merged_text, r.category
            FROM feedback_raw r
            WHERE r.category IS NOT NULL AND r.category != '-'
        ''')
        
        rows = cursor.fetchall()
        if conn != db.conn:
            conn.close()
        
        return [dict(row) for row in rows]
