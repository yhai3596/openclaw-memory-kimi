"""
数据库模型定义
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path="./data/feedback.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 原始反馈表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_raw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id VARCHAR(50),
                subject TEXT,
                description TEXT,
                ticket_type VARCHAR(50),
                model VARCHAR(100),
                model_serial VARCHAR(100),
                air_handler_model VARCHAR(100),
                air_handler_serial VARCHAR(100),
                region VARCHAR(100),
                created_at TIMESTAMP,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 分类结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_classified (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feedback_id INTEGER REFERENCES feedback_raw(id),
                is_quality_issue BOOLEAN,
                primary_category VARCHAR(50),
                secondary_category VARCHAR(50),
                severity INTEGER,
                confidence FLOAT,
                keywords TEXT,
                merged_text TEXT,
                needs_review BOOLEAN DEFAULT FALSE,
                reviewed_by VARCHAR(50),
                reviewed_at TIMESTAMP,
                model_version VARCHAR(50),
                classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 周统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start DATE,
                week_end DATE,
                total_count INTEGER,
                quality_count INTEGER,
                non_quality_count INTEGER,
                category_stats TEXT,
                model_stats TEXT,
                alert_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # QC 检讨记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qc_review (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category VARCHAR(50),
                model VARCHAR(100),
                feedback_ids TEXT,
                count INTEGER,
                severity_score INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                assigned_to VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_feedback(self, data):
        """插入原始反馈数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback_raw 
            (ticket_id, subject, description, ticket_type, model, model_serial,
             air_handler_model, air_handler_serial, region, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('ticket_id'),
            data.get('subject'),
            data.get('description'),
            data.get('ticket_type'),
            data.get('model'),
            data.get('model_serial'),
            data.get('air_handler_model'),
            data.get('air_handler_serial'),
            data.get('region'),
            data.get('created_at')
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return feedback_id
    
    def insert_classification(self, data):
        """插入分类结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback_classified
            (feedback_id, is_quality_issue, primary_category, secondary_category,
             severity, confidence, keywords, merged_text, model_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('feedback_id'),
            data.get('is_quality_issue'),
            data.get('primary_category'),
            data.get('secondary_category'),
            data.get('severity'),
            data.get('confidence'),
            json.dumps(data.get('keywords', [])),
            data.get('merged_text'),
            data.get('model_version')
        ))
        
        conn.commit()
        conn.close()
    
    def get_feedback_by_week(self, week_start, week_end):
        """获取一周内的反馈数据"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.*, c.is_quality_issue, c.primary_category, c.secondary_category,
                   c.severity, c.confidence, c.keywords, c.needs_review
            FROM feedback_raw r
            LEFT JOIN feedback_classified c ON r.id = c.feedback_id
            WHERE r.created_at >= ? AND r.created_at < ?
        ''', (week_start, week_end))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_unclassified_feedback(self):
        """获取未分类的反馈"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.* FROM feedback_raw r
            LEFT JOIN feedback_classified c ON r.id = c.feedback_id
            WHERE c.id IS NULL
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_review_status(self, classification_id, reviewed_by, status=True):
        """更新复核状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE feedback_classified
            SET needs_review = ?, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        ''', (not status, reviewed_by, datetime.now(), classification_id))
        
        conn.commit()
        conn.close()
    
    def insert_qc_review(self, data):
        """插入 QC 检讨记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO qc_review
            (category, model, feedback_ids, count, severity_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('category'),
            data.get('model'),
            json.dumps(data.get('feedback_ids', [])),
            data.get('count'),
            data.get('severity_score')
        ))
        
        conn.commit()
        conn.close()
    
    def get_qc_reviews(self, status=None):
        """获取 QC 检讨记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM qc_review WHERE status = ?', (status,))
        else:
            cursor.execute('SELECT * FROM qc_review')
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
