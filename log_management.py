#!/usr/bin/env python3
"""
Advanced Log Management System for Autonomous AI Systems
Handles log compression, archiving, database storage, and token usage monitoring
"""

import os
import gzip
import shutil
import sqlite3
import logging
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import hashlib

from token_manager import get_token_manager, TokenManager

# Configure logging for this module
logger = logging.getLogger(__name__)

@dataclass
class LogConfig:
    """Configuration for log management"""
    max_log_size_mb: int = 100
    max_log_age_days: int = 7
    compression_threshold_days: int = 1
    archive_threshold_days: int = 30
    db_batch_size: int = 1000
    token_monitoring_enabled: bool = True
    max_tokens_per_hour: int = 100000
    compression_ratio_target: float = 0.1  # Target 90% compression

class LogManager:
    """Advanced log management system with compression, archiving, and database storage"""
    
    def __init__(self, config: LogConfig = None, db_path: str = None):
        self.config = config or LogConfig()
        self.db_path = db_path or "db/log_management.db"
        self.token_manager = get_token_manager()
        self.token_usage_cache = defaultdict(int)
        self.token_usage_hourly = defaultdict(int)
        self.compression_stats = defaultdict(int)
        self._init_database()
        self._start_background_tasks()
        
        logger.info(f"LogManager initialized with database: {self.db_path}")
    
    def _init_database(self):
        """Initialize the log management database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Main logs table - stores important logs in database
        cur.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                logger_name TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                function TEXT,
                line_number INTEGER,
                exception_info TEXT,
                extra_data TEXT,
                log_hash TEXT UNIQUE,
                compressed_size INTEGER,
                original_size INTEGER,
                token_count INTEGER,
                archived BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Token usage tracking table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                model_name TEXT,
                prompt_tokens INTEGER,
                response_tokens INTEGER,
                total_tokens INTEGER,
                cost_estimate REAL,
                efficiency_ratio REAL,
                context_type TEXT,
                session_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Compression and archiving statistics
        cur.execute('''
            CREATE TABLE IF NOT EXISTS compression_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_size INTEGER,
                compressed_size INTEGER,
                compression_ratio REAL,
                compression_method TEXT,
                archived BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Log metadata and indexing
        cur.execute('''
            CREATE TABLE IF NOT EXISTS log_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER,
                key TEXT NOT NULL,
                value TEXT,
                FOREIGN KEY (log_id) REFERENCES system_logs (id)
            )
        ''')
        
        # Create indexes for performance
        cur.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_logs_logger ON system_logs(logger_name)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp ON token_usage(timestamp)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_compression_stats_timestamp ON compression_stats(timestamp)')
        
        conn.commit()
        conn.close()
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        def maintenance_loop():
            while True:
                try:
                    self._perform_maintenance()
                    time.sleep(3600)  # Run every hour
                except Exception as e:
                    logger.error(f"Error in maintenance loop: {e}")
                    time.sleep(300)  # Wait 5 minutes on error
        
        maintenance_thread = threading.Thread(target=maintenance_loop, daemon=True)
        maintenance_thread.start()
    
    def store_log_in_db(self, record: logging.LogRecord, extra_data: Dict = None):
        """Store important log entries in database for efficient querying"""
        try:
            # Calculate log hash for deduplication
            log_content = f"{record.created}:{record.levelname}:{record.getMessage()}"
            log_hash = hashlib.md5(log_content.encode()).hexdigest()
            
            # Count tokens in the log message
            token_count = self.token_manager.count_tokens(record.getMessage())
            
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Check if log already exists
            cur.execute('SELECT id FROM system_logs WHERE log_hash = ?', (log_hash,))
            if cur.fetchone():
                conn.close()
                return
            
            # Extract exception info if present
            exception_info = None
            if record.exc_info:
                exception_info = logging.Formatter().formatException(record.exc_info)
            
            cur.execute('''
                INSERT INTO system_logs (
                    timestamp, level, logger_name, message, module, function,
                    line_number, exception_info, extra_data, log_hash, token_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.fromtimestamp(record.created).isoformat(),
                record.levelname,
                record.name,
                record.getMessage(),
                record.module,
                record.funcName,
                record.lineno,
                exception_info,
                json.dumps(extra_data) if extra_data else None,
                log_hash,
                token_count
            ))
            
            conn.commit()
            conn.close()
            
            # Update token usage tracking
            if self.config.token_monitoring_enabled:
                self._track_token_usage('log_storage', token_count)
            
        except Exception as e:
            logger.error(f"Failed to store log in database: {e}")
    
    def track_token_usage(self, operation: str, prompt_tokens: int, 
                         response_tokens: int = 0, model_name: str = None,
                         context_type: str = None, session_id: str = None):
        """Track token usage for AI operations"""
        if not self.config.token_monitoring_enabled:
            return
        
        try:
            total_tokens = prompt_tokens + response_tokens
            efficiency = response_tokens / max(prompt_tokens, 1)
            
            # Calculate cost estimate (rough approximation)
            cost_per_1k_tokens = 0.01  # Adjust based on your models
            cost_estimate = (total_tokens / 1000) * cost_per_1k_tokens
            
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO token_usage (
                    timestamp, operation, model_name, prompt_tokens, 
                    response_tokens, total_tokens, cost_estimate, efficiency_ratio,
                    context_type, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                operation,
                model_name or "unknown",
                prompt_tokens,
                response_tokens,
                total_tokens,
                cost_estimate,
                efficiency,
                context_type,
                session_id
            ))
            
            conn.commit()
            conn.close()
            
            # Update cache for real-time monitoring
            current_hour = datetime.now().strftime("%Y-%m-%d-%H")
            self.token_usage_hourly[current_hour] += total_tokens
            
            # Check if we're approaching limits
            if self.token_usage_hourly[current_hour] > self.config.max_tokens_per_hour * 0.8:
                logger.warning(f"Approaching token limit: {self.token_usage_hourly[current_hour]} tokens this hour")
            
        except Exception as e:
            logger.error(f"Failed to track token usage: {e}")
    
    def _track_token_usage(self, operation: str, tokens: int):
        """Internal method for tracking token usage"""
        current_hour = datetime.now().strftime("%Y-%m-%d-%H")
        self.token_usage_cache[current_hour] += tokens
    
    def compress_old_logs(self, days_old: int = None):
        """Compress log files older than specified days"""
        days_old = days_old or self.config.compression_threshold_days
        
        try:
            log_dir = Path(".")
            current_time = datetime.now()
            
            for log_file in log_dir.glob("*.log"):
                if log_file.is_file():
                    file_age = current_time - datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_age.days >= days_old and not log_file.name.endswith('.gz'):
                        self._compress_log_file(log_file)
            
            # Also compress intelligence reports
            for report_file in log_dir.glob("intelligence_report_*.json"):
                file_age = current_time - datetime.fromtimestamp(report_file.stat().st_mtime)
                
                if file_age.days >= days_old:
                    self._compress_json_file(report_file)
            
            logger.info(f"Completed compression of logs older than {days_old} days")
            
        except Exception as e:
            logger.error(f"Error during log compression: {e}")
    
    def _compress_log_file(self, file_path: Path):
        """Compress a single log file"""
        try:
            original_size = file_path.stat().st_size
            
            # Create compressed version
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=9) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = compressed_path.stat().st_size
            compression_ratio = compressed_size / original_size
            
            # Store compression statistics
            self._store_compression_stats(str(file_path), original_size, 
                                         compressed_size, compression_ratio, 'gzip')
            
            # Remove original file if compression was successful
            if compression_ratio < 0.5:  # At least 50% compression
                file_path.unlink()
                logger.info(f"Compressed {file_path.name}: {original_size} -> {compressed_size} bytes "
                          f"({compression_ratio:.1%} ratio)")
            else:
                compressed_path.unlink()  # Remove compressed version if not effective
                logger.warning(f"Compression not effective for {file_path.name}, keeping original")
            
        except Exception as e:
            logger.error(f"Failed to compress {file_path}: {e}")
    
    def _compress_json_file(self, file_path: Path):
        """Compress JSON intelligence reports"""
        try:
            # Read and re-serialize JSON for better compression
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Create compressed version
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with gzip.open(compressed_path, 'wt', compresslevel=9) as f:
                json.dump(data, f, separators=(',', ':'), sort_keys=True)
            
            original_size = file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            compression_ratio = compressed_size / original_size
            
            self._store_compression_stats(str(file_path), original_size, 
                                         compressed_size, compression_ratio, 'json_gzip')
            
            # Remove original if compression was successful
            if compression_ratio < 0.3:  # JSON can compress very well
                file_path.unlink()
                logger.info(f"Compressed JSON {file_path.name}: {original_size} -> {compressed_size} bytes")
            
        except Exception as e:
            logger.error(f"Failed to compress JSON file {file_path}: {e}")
    
    def _store_compression_stats(self, file_path: str, original_size: int, 
                                compressed_size: int, compression_ratio: float, 
                                method: str):
        """Store compression statistics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute('''
                INSERT INTO compression_stats (
                    timestamp, file_path, original_size, compressed_size, 
                    compression_ratio, compression_method
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                file_path,
                original_size,
                compressed_size,
                compression_ratio,
                method
            ))
            
            conn.commit()
            conn.close()
            
            # Update in-memory stats
            self.compression_stats['total_files'] += 1
            self.compression_stats['total_bytes_saved'] += (original_size - compressed_size)
            
        except Exception as e:
            logger.error(f"Failed to store compression stats: {e}")
    
    def archive_old_logs(self, days_old: int = None):
        """Archive very old logs to long-term storage"""
        days_old = days_old or self.config.archive_threshold_days
        
        try:
            archive_dir = Path("archives")
            archive_dir.mkdir(exist_ok=True)
            
            current_time = datetime.now()
            archive_date = current_time.strftime("%Y%m%d")
            
            # Create archive subdirectory
            archive_subdir = archive_dir / f"logs_archive_{archive_date}"
            archive_subdir.mkdir(exist_ok=True)
            
            # Archive old log files
            log_dir = Path(".")
            archived_count = 0
            
            for log_file in log_dir.glob("*.log.gz"):
                file_age = current_time - datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_age.days >= days_old:
                    # Move to archive directory
                    archive_path = archive_subdir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    archived_count += 1
                    
                    # Update database records
                    self._mark_as_archived(str(log_file))
            
            # Create archive metadata
            archive_metadata = {
                'archive_date': archive_date,
                'archived_files': archived_count,
                'total_size_mb': sum(f.stat().st_size for f in archive_subdir.glob("*.gz")) / (1024 * 1024),
                'compression_method': 'gzip',
                'retention_policy': f"Keep for {days_old} days before archiving"
            }
            
            with open(archive_subdir / "archive_metadata.json", 'w') as f:
                json.dump(archive_metadata, f, indent=2)
            
            logger.info(f"Archived {archived_count} files to {archive_subdir}")
            
        except Exception as e:
            logger.error(f"Error during log archiving: {e}")
    
    def _mark_as_archived(self, file_path: str):
        """Mark logs as archived in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cur.execute('''
                UPDATE system_logs SET archived = 1 
                WHERE message LIKE ? OR extra_data LIKE ?
            ''', (f"%{file_path}%", f"%{file_path}%"))
            
            cur.execute('''
                UPDATE compression_stats SET archived = 1 
                WHERE file_path = ?
            ''', (file_path,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to mark as archived: {e}")
    
    def cleanup_old_logs(self, days_old: int = None):
        """Remove very old logs that are no longer needed"""
        days_old = days_old or (self.config.archive_threshold_days + 30)
        
        try:
            current_time = datetime.now()
            removed_count = 0
            
            # Clean up old compressed logs
            for log_file in Path(".").glob("*.log.gz"):
                file_age = current_time - datetime.fromtimestamp(log_file.stat().st_mtime)
                
                if file_age.days >= days_old:
                    log_file.unlink()
                    removed_count += 1
            
            # Clean up old archives
            archive_dir = Path("archives")
            if archive_dir.exists():
                for archive_subdir in archive_dir.glob("logs_archive_*"):
                    dir_age = current_time - datetime.fromtimestamp(archive_subdir.stat().st_mtime)
                    
                    if dir_age.days >= days_old:
                        shutil.rmtree(archive_subdir)
                        removed_count += 1
            
            # Clean up old database records
            self._cleanup_old_db_records(days_old)
            
            logger.info(f"Cleaned up {removed_count} old log files and records")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _cleanup_old_db_records(self, days_old: int):
        """Clean up old database records"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            # Remove old non-critical logs
            cur.execute('''
                DELETE FROM system_logs 
                WHERE timestamp < ? AND level IN ('DEBUG', 'INFO') AND archived = 1
            ''', (cutoff_date,))
            
            # Remove old token usage records
            cur.execute('''
                DELETE FROM token_usage 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            # Remove old compression stats
            cur.execute('''
                DELETE FROM compression_stats 
                WHERE timestamp < ? AND archived = 1
            ''', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to cleanup database records: {e}")
    
    def _perform_maintenance(self):
        """Perform regular maintenance tasks"""
        try:
            logger.info("Starting log maintenance tasks")
            
            # Compress old logs
            self.compress_old_logs()
            
            # Archive very old logs
            self.archive_old_logs()
            
            # Cleanup extremely old logs
            self.cleanup_old_logs()
            
            # Log maintenance statistics
            self._log_maintenance_stats()
            
        except Exception as e:
            logger.error(f"Error during maintenance: {e}")
    
    def _log_maintenance_stats(self):
        """Log maintenance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Get database statistics
            cur.execute('SELECT COUNT(*) FROM system_logs')
            total_logs = cur.fetchone()[0]
            
            cur.execute('SELECT COUNT(*) FROM token_usage')
            total_token_records = cur.fetchone()[0]
            
            cur.execute('SELECT SUM(total_tokens) FROM token_usage')
            total_tokens_used = cur.fetchone()[0] or 0
            
            cur.execute('SELECT COUNT(*) FROM compression_stats WHERE archived = 0')
            active_compressed_files = cur.fetchone()[0]
            
            conn.close()
            
            # Calculate space savings
            space_saved_mb = self.compression_stats.get('total_bytes_saved', 0) / (1024 * 1024)
            
            logger.info(f"Maintenance stats: {total_logs} logs, {total_token_records} token records, "
                      f"{total_tokens_used:,} total tokens, {space_saved_mb:.1f}MB space saved, "
                      f"{active_compressed_files} compressed files")
            
        except Exception as e:
            logger.error(f"Failed to log maintenance stats: {e}")
    
    def get_token_usage_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get token usage report for the specified hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cur.execute('''
                SELECT 
                    COUNT(*) as total_operations,
                    SUM(total_tokens) as total_tokens,
                    AVG(total_tokens) as avg_tokens_per_operation,
                    SUM(cost_estimate) as total_cost,
                    AVG(efficiency_ratio) as avg_efficiency
                FROM token_usage
                WHERE timestamp > ?
            ''', (cutoff_time,))
            
            stats = cur.fetchone()
            
            # Get hourly breakdown
            cur.execute('''
                SELECT 
                    strftime('%Y-%m-%d %H:00', timestamp) as hour,
                    SUM(total_tokens) as tokens_per_hour
                FROM token_usage
                WHERE timestamp > ?
                GROUP BY hour
                ORDER BY hour DESC
            ''', (cutoff_time,))
            
            hourly_breakdown = cur.fetchall()
            
            conn.close()
            
            return {
                'period_hours': hours,
                'total_operations': stats[0] or 0,
                'total_tokens': stats[1] or 0,
                'avg_tokens_per_operation': stats[2] or 0,
                'total_cost': stats[3] or 0,
                'avg_efficiency': stats[4] or 0,
                'hourly_breakdown': hourly_breakdown,
                'token_limit_status': 'ok' if stats[1] < self.config.max_tokens_per_hour else 'limit_exceeded'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate token usage report: {e}")
            return {}
    
    def query_logs(self, level: str = None, logger_name: str = None, 
                  start_time: str = None, end_time: str = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """Query logs from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            query = '''
                SELECT timestamp, level, logger_name, message, module, 
                       function, line_number, exception_info, extra_data
                FROM system_logs
                WHERE 1=1
            '''
            params = []
            
            if level:
                query += ' AND level = ?'
                params.append(level)
            
            if logger_name:
                query += ' AND logger_name LIKE ?'
                params.append(f'%{logger_name}%')
            
            if start_time:
                query += ' AND timestamp >= ?'
                params.append(start_time)
            
            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cur.execute(query, params)
            rows = cur.fetchall()
            
            conn.close()
            
            logs = []
            for row in rows:
                logs.append({
                    'timestamp': row[0],
                    'level': row[1],
                    'logger_name': row[2],
                    'message': row[3],
                    'module': row[4],
                    'function': row[5],
                    'line_number': row[6],
                    'exception_info': row[7],
                    'extra_data': json.loads(row[8]) if row[8] else None
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to query logs: {e}")
            return []

# Global log manager instance
_log_manager = None

def get_log_manager(config: LogConfig = None, db_path: str = None) -> LogManager:
    """Get or create global log manager instance"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager(config, db_path)
    return _log_manager

# Custom logging handler that integrates with the log management system
class DatabaseLogHandler(logging.Handler):
    """Custom logging handler that stores important logs in database"""
    
    def __init__(self, log_manager: LogManager = None):
        super().__init__()
        self.log_manager = log_manager or get_log_manager()
    
    def emit(self, record):
        """Store log record in database"""
        try:
            # Only store logs above WARNING level in database
            if record.levelno >= logging.WARNING:
                self.log_manager.store_log_in_db(record)
        except Exception as e:
            # Don't let logging errors break the main application
            print(f"Failed to store log in database: {e}")

if __name__ == "__main__":
    # Test the log management system
    logging.basicConfig(level=logging.INFO)
    
    print("🗄️ Testing Log Management System")
    print("=" * 50)
    
    # Create log manager
    log_manager = LogManager()
    
    # Test token usage tracking
    log_manager.track_token_usage("test_operation", 100, 200, "test-model")
    
    # Test log storage
    test_record = logging.LogRecord(
        name="test_logger", level=logging.ERROR, pathname="test.py",
        lineno=1, msg="Test error message", args=(), exc_info=None
    )
    log_manager.store_log_in_db(test_record)
    
    # Test compression stats
    log_manager._store_compression_stats("test.log", 1000, 100, 0.1, "gzip")
    
    # Test token usage report
    report = log_manager.get_token_usage_report(1)
    print(f"Token usage report: {report}")
    
    print("✅ Log management system tests complete!")
