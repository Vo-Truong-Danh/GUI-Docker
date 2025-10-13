"""
Database Layer - Job History & Metrics Storage
Version: 4.4.0
"""

import sqlite3
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import os


class DatabaseManager:
    """SQLite database manager for application data"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_dir = Path(__file__).parent
            db_path = db_dir / 'spark_runner.db'
        
        self.db_path = str(db_path)
        self.lock = threading.Lock()
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database schema"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Job History Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    container TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL,
                    exit_code INTEGER,
                    output TEXT,
                    error TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Upload History Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS upload_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    container TEXT NOT NULL,
                    hdfs_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration REAL,
                    error TEXT,
                    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance Metrics Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    container TEXT,
                    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User Preferences Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # AI Code Generation History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_code_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_type TEXT NOT NULL,
                    job_name TEXT NOT NULL,
                    input_file TEXT NOT NULL,
                    output_path TEXT NOT NULL,
                    generated_code TEXT NOT NULL,
                    parameters TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_job_history_status 
                ON job_history(status)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_job_history_start_time 
                ON job_history(start_time DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_upload_history_status 
                ON upload_history(status)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_name_time 
                ON performance_metrics(metric_name, recorded_at DESC)
            ''')
            
            conn.commit()
            conn.close()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    # ==== Job History Methods ====
    
    def add_job(self, job_data: Dict[str, Any]) -> int:
        """Add job to history"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO job_history 
                (job_name, file_path, container, status, start_time, end_time, 
                 duration, exit_code, output, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('job_name'),
                job_data.get('file_path'),
                job_data.get('container'),
                job_data.get('status'),
                job_data.get('start_time'),
                job_data.get('end_time'),
                job_data.get('duration'),
                job_data.get('exit_code'),
                job_data.get('output'),
                job_data.get('error')
            ))
            
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return job_id
    
    def update_job(self, job_id: int, updates: Dict[str, Any]):
        """Update job record"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [job_id]
            
            cursor.execute(f'''
                UPDATE job_history 
                SET {set_clause}
                WHERE id = ?
            ''', values)
            
            conn.commit()
            conn.close()
    
    def get_job_history(self, limit: int = 50, status: str = None) -> List[Dict]:
        """Get job history"""
        with self.lock:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM job_history 
                    WHERE status = ?
                    ORDER BY start_time DESC 
                    LIMIT ?
                ''', (status, limit))
            else:
                cursor.execute('''
                    SELECT * FROM job_history 
                    ORDER BY start_time DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
    
    def get_job_stats(self) -> Dict[str, Any]:
        """Get job statistics"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    AVG(CASE WHEN duration IS NOT NULL THEN duration ELSE 0 END) as avg_duration,
                    MAX(duration) as max_duration,
                    MIN(duration) as min_duration
                FROM job_history
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_jobs': row[0] or 0,
                'successful': row[1] or 0,
                'failed': row[2] or 0,
                'avg_duration': row[3] or 0,
                'max_duration': row[4] or 0,
                'min_duration': row[5] or 0
            }
    
    # ==== Upload History Methods ====
    
    def add_upload(self, upload_data: Dict[str, Any]) -> int:
        """Add upload to history"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO upload_history 
                (file_name, file_size, container, hdfs_path, status, duration, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                upload_data.get('file_name'),
                upload_data.get('file_size'),
                upload_data.get('container'),
                upload_data.get('hdfs_path'),
                upload_data.get('status'),
                upload_data.get('duration'),
                upload_data.get('error')
            ))
            
            upload_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return upload_id
    
    def get_upload_history(self, limit: int = 50) -> List[Dict]:
        """Get upload history"""
        with self.lock:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM upload_history 
                ORDER BY uploaded_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """Get upload statistics"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_uploads,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(file_size) as total_size,
                    AVG(duration) as avg_duration
                FROM upload_history
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                'total_uploads': row[0] or 0,
                'successful': row[1] or 0,
                'failed': row[2] or 0,
                'total_size': row[3] or 0,
                'avg_duration': row[4] or 0
            }
    
    # ==== Performance Metrics Methods ====
    
    def record_metric(self, metric_name: str, value: float, unit: str = None, container: str = None):
        """Record performance metric"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (metric_name, metric_value, metric_unit, container)
                VALUES (?, ?, ?, ?)
            ''', (metric_name, value, unit, container))
            
            conn.commit()
            conn.close()
    
    def get_metrics(self, metric_name: str, limit: int = 100) -> List[Dict]:
        """Get metrics history"""
        with self.lock:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM performance_metrics 
                WHERE metric_name = ?
                ORDER BY recorded_at DESC 
                LIMIT ?
            ''', (metric_name, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
    
    # ==== User Preferences Methods ====
    
    def set_preference(self, key: str, value: Any):
        """Set user preference"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convert value to JSON string if not string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
            conn.close()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value FROM user_preferences WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                return default
            
            # Try to parse as JSON
            try:
                return json.loads(row[0])
            except:
                return row[0]
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all preferences"""
        with self.lock:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT key, value FROM user_preferences')
            rows = cursor.fetchall()
            conn.close()
            
            prefs = {}
            for row in rows:
                key = row['key']
                value = row['value']
                try:
                    prefs[key] = json.loads(value)
                except:
                    prefs[key] = value
            
            return prefs
    
    # ==== AI Code History Methods ====
    
    def save_generated_code(self, code_data: Dict[str, Any]) -> int:
        """Save generated code"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_code_history 
                (template_type, job_name, input_file, output_path, 
                 generated_code, parameters)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                code_data.get('template_type'),
                code_data.get('job_name'),
                code_data.get('input_file'),
                code_data.get('output_path'),
                code_data.get('generated_code'),
                json.dumps(code_data.get('parameters', {}))
            ))
            
            code_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return code_id
    
    def get_code_history(self, limit: int = 20) -> List[Dict]:
        """Get AI code generation history"""
        with self.lock:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ai_code_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                item = dict(row)
                try:
                    item['parameters'] = json.loads(item['parameters'])
                except:
                    item['parameters'] = {}
                history.append(item)
            
            return history
    
    # ==== Utility Methods ====
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete old job history
            cursor.execute('''
                DELETE FROM job_history 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            # Delete old upload history
            cursor.execute('''
                DELETE FROM upload_history 
                WHERE uploaded_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            # Delete old metrics
            cursor.execute('''
                DELETE FROM performance_metrics 
                WHERE recorded_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            conn.commit()
            conn.close()
    
    def export_to_json(self, output_file: str):
        """Export database to JSON"""
        data = {
            'job_history': self.get_job_history(limit=1000),
            'upload_history': self.get_upload_history(limit=1000),
            'job_stats': self.get_job_stats(),
            'upload_stats': self.get_upload_stats(),
            'preferences': self.get_all_preferences(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def close(self):
        """Close database"""
        # Connection is closed after each operation
        pass


# Global database instance
db = DatabaseManager()


if __name__ == '__main__':
    # Test database operations
    print("Testing Database System...")
    
    # Test job history
    job_id = db.add_job({
        'job_name': 'test_job',
        'file_path': '/path/to/test.py',
        'container': 'spark-worker',
        'status': 'success',
        'start_time': datetime.now().isoformat(),
        'end_time': datetime.now().isoformat(),
        'duration': 10.5,
        'exit_code': 0,
        'output': 'Job completed successfully',
        'error': None
    })
    print(f"✓ Added job with ID: {job_id}")
    
    # Test upload history
    upload_id = db.add_upload({
        'file_name': 'test.csv',
        'file_size': 1024,
        'container': 'namenode',
        'hdfs_path': '/data/test.csv',
        'status': 'success',
        'duration': 5.2,
        'error': None
    })
    print(f"✓ Added upload with ID: {upload_id}")
    
    # Test metrics
    db.record_metric('cpu_usage', 45.5, '%', 'spark-master')
    print("✓ Recorded metric")
    
    # Test preferences
    db.set_preference('theme', 'dark')
    db.set_preference('auto_refresh', True)
    theme = db.get_preference('theme')
    print(f"✓ Set preference theme: {theme}")
    
    # Get stats
    job_stats = db.get_job_stats()
    print(f"✓ Job stats: {job_stats}")
    
    upload_stats = db.get_upload_stats()
    print(f"✓ Upload stats: {upload_stats}")
    
    print("\n✓ All database tests passed!")
