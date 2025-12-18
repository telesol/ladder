#!/usr/bin/env python3
"""
System health check for upgraded logging system
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_integration import get_system_logger, get_ai_logger
from log_management import get_log_manager
from token_manager import get_token_manager

def check_system_health():
    """Check overall system health"""
    print(f"🏥 System Health Check - {datetime.now()}")
    print("=" * 50)
    
    # Check log managers
    system_logger = get_system_logger()
    ai_logger = get_ai_logger()
    log_manager = get_log_manager()
    
    # Check token usage
    token_summary = ai_logger.get_token_usage_summary(24)  # Last 24 hours
    print(f"📊 Token Usage (24h):")
    print(f"  Total operations: {token_summary.get('total_operations', 0)}")
    print(f"  Total tokens: {token_summary.get('total_tokens', 0):,}")
    print(f"  Average per operation: {token_summary.get('avg_tokens_per_operation', 0):.1f}")
    print(f"  Status: {token_summary.get('token_limit_status', 'unknown')}")
    
    # Check recent logs
    recent_logs = system_logger.get_recent_logs(limit=5)
    print(f"\n📋 Recent System Logs:")
    for log in recent_logs:
        print(f"  {log['timestamp']} - {log['level']} - {log['message'][:60]}...")
    
    # Check disk usage
    log_dir = Path("logs")
    if log_dir.exists():
        total_size = sum(f.stat().st_size for f in log_dir.glob("**/*") if f.is_file())
        print(f"\n💾 Disk Usage:")
        print(f"  Log directory size: {total_size / (1024*1024):.1f} MB")
    
    # Check compression status
    compressed_files = list(Path(".").glob("*.gz"))
    archive_dirs = list(Path("archives").glob("logs_archive_*")) if Path("archives").exists() else []
    print(f"\n🗜️ Compression Status:")
    print(f"  Compressed files: {len(compressed_files)}")
    print(f"  Archive directories: {len(archive_dirs)}")
    
    print("\n✅ Health check complete")

if __name__ == "__main__":
    check_system_health()
