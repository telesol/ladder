#!/usr/bin/env python3
"""
System upgrade script to integrate log management with existing autonomous AI system
This script upgrades the current system to use the new log management features
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_integration import upgrade_system_logging, get_system_logger, get_ai_logger, get_memory_logger
from log_management import get_log_manager, LogConfig
from token_manager import get_token_manager

def backup_existing_logs():
    """Backup existing log files before upgrade"""
    print("📋 Backing up existing log files...")
    
    # Create backup directory
    backup_dir = Path(f"log_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    # Find and backup log files
    log_patterns = ["*.log", "intelligence_report_*.json", "*.log.gz"]
    backed_up_files = 0
    
    for pattern in log_patterns:
        for log_file in Path(".").glob(pattern):
            if log_file.is_file():
                shutil.copy2(log_file, backup_dir / log_file.name)
                backed_up_files += 1
    
    print(f"✅ Backed up {backed_up_files} files to {backup_dir}")
    return backup_dir

def upgrade_existing_files():
    """Upgrade existing system files to use integrated logging"""
    print("🔧 Upgrading existing system files...")
    
    # Files to upgrade
    files_to_upgrade = [
        "final_autonomous_system.py",
        "agent_orchestrator_v2.py",
        "memory_system.py",
        "daemon_autonomous.py",
        "agents/autonomous_orchestrator.py",
        "agents/intelligent_mathematician.py",
        "agents/discovery_agent.py",
        "agents/verification_agent.py",
    ]
    
    upgraded_files = []
    
    for file_path in files_to_upgrade:
        if Path(file_path).exists():
            print(f"  Upgrading {file_path}...")
            
            # Read the file
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add import statement
            if "from log_integration import" not in content:
                # Find the first import section
                import_section_end = content.find("import") + content[content.find("import"):].find("\n") + 1
                if import_section_end > 0:
                    new_content = (
                        content[:import_section_end] +
                        "from log_integration import get_system_logger, get_ai_logger, get_memory_logger\n" +
                        content[import_section_end:]
                    )
                    content = new_content
            
            # Replace basic logging with integrated logging
            replacements = [
                ("logging\\.getLogger\\(.*\\)", "get_system_logger().logger"),
                ("logging\\.info\\(", "get_system_logger().logger.info("),
                ("logging\\.warning\\(", "get_system_logger().logger.warning("),
                ("logging\\.error\\(", "get_system_logger().logger.error("),
                ("logging\\.debug\\(", "get_system_logger().logger.debug("),
            ]
            
            for pattern, replacement in replacements:
                import re
                content = re.sub(pattern, replacement, content)
            
            # Write back to file
            with open(file_path, 'w') as f:
                f.write(content)
            
            upgraded_files.append(file_path)
    
    print(f"✅ Upgraded {len(upgraded_files)} files")
    return upgraded_files

def integrate_token_monitoring():
    """Integrate token monitoring into AI operations"""
    print("🧮 Integrating token monitoring...")
    
    # Create token monitoring configuration
    log_manager = get_log_manager(
        config=LogConfig(
            token_monitoring_enabled=True,
            max_tokens_per_hour=50000  # Reasonable limit for production
        )
    )
    
    print("✅ Token monitoring integrated with limits:")
    print(f"  - Hourly limit: {log_manager.config.max_tokens_per_hour:,} tokens")

def setup_log_directories():
    """Setup necessary log directories"""
    print("📁 Setting up log directories...")
    
    directories = [
        "logs",
        "archives",
        "logs/compressed",
        "logs/database",
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  Created {directory}")
    
    print("✅ Log directories setup complete")

def create_system_health_check():
    """Create system health check script"""
    print("🏥 Creating system health check...")
    
    health_check_script = '''#!/usr/bin/env python3
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
    print(f"\\n📋 Recent System Logs:")
    for log in recent_logs:
        print(f"  {log['timestamp']} - {log['level']} - {log['message'][:60]}...")
    
    # Check disk usage
    log_dir = Path("logs")
    if log_dir.exists():
        total_size = sum(f.stat().st_size for f in log_dir.glob("**/*") if f.is_file())
        print(f"\\n💾 Disk Usage:")
        print(f"  Log directory size: {total_size / (1024*1024):.1f} MB")
    
    # Check compression status
    compressed_files = list(Path(".").glob("*.gz"))
    archive_dirs = list(Path("archives").glob("logs_archive_*")) if Path("archives").exists() else []
    print(f"\\n🗜️ Compression Status:")
    print(f"  Compressed files: {len(compressed_files)}")
    print(f"  Archive directories: {len(archive_dirs)}")
    
    print("\\n✅ Health check complete")

if __name__ == "__main__":
    check_system_health()
'''
    
    with open("system_health_check.py", 'w') as f:
        f.write(health_check_script)
    
    # Make it executable
    os.chmod("system_health_check.py", 0o755)
    
    print("✅ System health check script created")

def main():
    """Main upgrade process"""
    print("🚀 Starting System Logging Upgrade")
    print("=" * 50)
    
    try:
        # Backup existing logs
        backup_dir = backup_existing_logs()
        
        # Setup directories
        setup_log_directories()
        
        # Upgrade system logging
        upgrade_system_logging()
        
        # Upgrade existing files
        upgraded_files = upgrade_existing_files()
        
        # Integrate token monitoring
        integrate_token_monitoring()
        
        # Create health check
        create_system_health_check()
        
        print("\n" + "=" * 50)
        print("✅ SYSTEM UPGRADE COMPLETE!")
        print("=" * 50)
        print(f"📋 Backup created: {backup_dir}")
        print(f"🔧 Files upgraded: {len(upgraded_files)}")
        print(f"🧮 Token monitoring: Enabled with limits")
        print(f"📁 Log directories: Created and configured")
        print(f"🏥 Health check: Available as system_health_check.py")
        
        print("\n🎯 Next Steps:")
        print("1. Run 'python3 system_health_check.py' to verify the upgrade")
        print("2. Test your autonomous system to ensure logging works correctly")
        print("3. Monitor token usage with the new limits in place")
        print("4. Check compressed logs in archives/ directory periodically")
        
        print("\n⚠️  Important Notes:")
        print("- Token limits are set to prevent excessive AI usage")
        print("- Old log files are backed up in case of issues")
        print("- Database logging is enabled for important events")
        print("- Compression will run automatically for old logs")
        
    except Exception as e:
        print(f"\n❌ Upgrade failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
