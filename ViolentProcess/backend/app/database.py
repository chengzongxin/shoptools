"""
数据库配置和初始化
使用SQLite作为本地数据库，存储违规记录、操作历史等数据
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

# 数据库文件路径
DB_PATH = Path("data/temu_toolkit.db")
DATA_DIR = Path("data")

class Database:
    """数据库操作类"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        DATA_DIR.mkdir(exist_ok=True)
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        return conn
    
    def init_tables(self):
        """初始化数据库表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 违规记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spuid TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                violation_type TEXT,
                violation_date TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 搜索历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                search_type TEXT NOT NULL,  -- 'temu' 或 'blue'
                results_count INTEGER,
                search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 操作记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,  -- 'off_shelf', 'delete_image'
                target_id TEXT NOT NULL,
                target_name TEXT,
                status TEXT DEFAULT 'pending',  -- 'pending', 'success', 'failed'
                error_message TEXT,
                operation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()

# 全局数据库实例
db = Database()

async def init_db():
    """初始化数据库"""
    db.init_tables()
    print("数据库初始化完成")

def save_violation(spuid: str, product_name: str, violation_type: str = None, violation_date: str = None):
    """保存违规记录"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO violations (spuid, product_name, violation_type, violation_date)
            VALUES (?, ?, ?, ?)
        """, (spuid, product_name, violation_type, violation_date))
        conn.commit()
        return True
    except Exception as e:
        print(f"保存违规记录失败: {e}")
        return False
    finally:
        conn.close()

def get_violations(status: Optional[str] = None, limit: int = 100):
    """获取违规记录列表"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM violations"
    params = []
    
    if status:
        query += " WHERE status = ?"
        params.append(status)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

def save_search_history(keyword: str, search_type: str, results_count: int = 0):
    """保存搜索历史"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO search_history (keyword, search_type, results_count)
        VALUES (?, ?, ?)
    """, (keyword, search_type, results_count))
    
    conn.commit()
    conn.close()

def save_operation(operation_type: str, target_id: str, target_name: str = None):
    """保存操作记录"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO operations (operation_type, target_id, target_name)
        VALUES (?, ?, ?)
    """, (operation_type, target_id, target_name))
    
    conn.commit()
    conn.close()

def update_operation_status(operation_id: int, status: str, error_message: str = None):
    """更新操作状态"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE operations 
        SET status = ?, error_message = ?, operation_date = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, error_message, operation_id))
    
    conn.commit()
    conn.close()

def get_operations(operation_type: Optional[str] = None, limit: int = 50):
    """获取操作记录"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM operations"
    params = []
    
    if operation_type:
        query += " WHERE operation_type = ?"
        params.append(operation_type)
    
    query += " ORDER BY operation_date DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results 