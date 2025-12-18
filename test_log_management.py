#!/usr/bin/env python3
"""
Comprehensive test suite for the log management system
Tests compression, archiving, database storage, and token monitoring
"""

import os
import sys
import time
import json
import gzip
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from log_management import get_log_manager, LogConfig, DatabaseLogHandler
from log_integration import create_integrated_logger, get_system_logger, get_ai_logger
from token_manager import get_token_manager

def create_test_logs():
    """Create test log files for testing compression and archiving"""
    print("📝 Creating test log files...")
    
    # Create test directory
    test_dir = Path("test_logs")
    test_dir.mkdir(exist_ok=True)
    
    # Create various test log files
    test_files = [
        ("test_system.log", "System operation logs with performance metrics"),
        ("test_ai_operations.log", "AI model interactions and token usage"),
        ("test_memory.log", "Memory system operations and cache statistics"),
        ("test_errors.log", "Error logs and exception information"),
        ("intelligence_report_20251205_120000.json", '{"test": "intelligence data", "timestamp": "2025-12-05T12:00:00Z"}'),
        ("intelligence_report_20251205_130000.json", '{"test": "more intelligence data", "analysis": "complete", "score": 0.95}'),
    ]
    
    for filename, content in test_files:
        file_path = test_dir / filename
        with open(file_path, 'w') as f:
            if filename.endswith('.json'):
                f.write(content)
            else:
                # Generate realistic log content
                for i in range(100):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"{timestamp} - {filename.replace('.log', '').replace('test_', '').upper()} - Operation {i}: {content} - Status: {'SUCCESS' if i % 3 != 0 else 'WARNING' if i % 5 != 0 else 'ERROR'}\n"
                    f.write(log_entry)
    
    print(f"✅ Created {len(test_files)} test files in {test_dir}")

def test_token_monitoring():
    """Test token usage monitoring and limits"""
    print("🧮 Testing token monitoring...")
    
    log_manager = get_log_manager(
        config=LogConfig(
            token_monitoring_enabled=True,
            max_tokens_per_hour=1000  # Low limit for testing
        )
    )
    
    # Simulate AI operations
    operations = [
        ("hypothesis_generation", "Generate mathematical hypothesis for puzzle solving with multiple variables", "Hypothesis: The puzzle follows affine transformation pattern with modular arithmetic"),
        ("strategy_planning", "Plan attack strategy based on current puzzle state and available moves", "Strategy: Use intelligent mathematical attack with backtracking"),
        ("verification", "Verify the solution correctness using mathematical proofs", "Verification: Solution passes all mathematical constraints and boundary conditions"),
    ]
    
    total_tokens = 0
    for operation, prompt, response in operations:
        prompt_tokens = get_token_manager().count_tokens(prompt)
        response_tokens = get_token_manager().count_tokens(response)
        total_tokens += prompt_tokens + response_tokens
        
        log_manager.track_token_usage(
            operation=operation,
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            model_name="test-model",
            context_type="mathematical_analysis"
        )
    
    # Generate token usage report
    report = log_manager.get_token_usage_report(1)
    print(f"📊 Token usage report:")
    print(f"  Total operations: {report.get('total_operations', 0)}")
    print(f"  Total tokens: {report.get('total_tokens', 0)}")
    print(f"  Average tokens per operation: {report.get('avg_tokens_per_operation', 0):.1f}")
    print(f"  Token limit status: {report.get('token_limit_status', 'unknown')}")
    
    return report

def test_compression_and_archiving():
    """Test log compression and archiving functionality"""
    print("🗜️ Testing compression and archiving...")
    
    log_manager = get_log_manager()
    
    # Move test files to current directory for compression
    test_dir = Path("test_logs")
    for file_path in test_dir.glob("*"):
        if file_path.is_file():
            shutil.move(str(file_path), ".")
    
    # Test compression
    print("  Compressing old logs...")
    log_manager.compress_old_logs(days_old=0)  # Compress immediately for testing
    
    # Check compression results
    compressed_files = list(Path(".").glob("*.gz"))
    print(f"  Compressed {len(compressed_files)} files")
    
    # Verify compression effectiveness
    for compressed_file in compressed_files:
        original_file = compressed_file.with_suffix('')  # Remove .gz
        if original_file.exists():
            original_size = original_file.stat().st_size
            compressed_size = compressed_file.stat().st_size
            ratio = compressed_size / original_size
            print(f"    {compressed_file.name}: {original_size} → {compressed_size} bytes ({ratio:.1%} ratio)")
    
    # Test archiving
    print("  Archiving compressed logs...")
    log_manager.archive_old_logs(days_old=0)  # Archive immediately for testing
    
    # Check archive directory
    archive_dir = Path("archives")
    if archive_dir.exists():
        archive_subdirs = list(archive_dir.glob("logs_archive_*"))
        print(f"  Created {len(archive_subdirs)} archive directories")
        
        for archive_subdir in archive_subdirs:
            archived_files = list(archive_subdir.glob("*.gz"))
            print(f"    {archive_subdir.name}: {len(archived_files)} files")
    
    return len(compressed_files)

def test_database_logging():
    """Test database logging and querying"""
    print("🗄️ Testing database logging...")
    
    # Create integrated logger
    logger = create_integrated_logger("test_logger", logging.DEBUG)
    
    # Log various types of events
    logger.logger.info("Test information message")
    logger.logger.warning("Test warning message")
    logger.logger.error("Test error message")
    
    # Log AI operations
    logger.log_ai_operation(
        operation="test_analysis",
        prompt="Analyze the current puzzle state and determine optimal next move",
        response="Analysis complete: Recommended move is to apply modular arithmetic transformation",
        model_name="test-model",
        context_type="puzzle_analysis"
    )
    
    # Log system events
    logger.log_system_event(
        event_type="test_event",
        description="Testing system event logging",
        data={"test_key": "test_value", "timestamp": datetime.now().isoformat()},
        importance=8
    )
    
    # Query logs from database
    recent_logs = logger.get_recent_logs(limit=10)
    print(f"  Retrieved {len(recent_logs)} recent logs from database")
    
    for log in recent_logs[:3]:  # Show first 3 logs
        print(f"    {log['timestamp']} - {log['level']} - {log['message'][:80]}...")
    
    return len(recent_logs)

def test_integrated_logging():
    """Test the integrated logging system"""
    print("🔗 Testing integrated logging system...")
    
    # Create different types of loggers
    system_logger = get_system_logger()
    ai_logger = get_ai_logger()
    
    # Test system logging
    system_logger.logger.info("System initialization complete")
    system_logger.log_system_event(
        event_type="system_startup",
        description="Autonomous system started successfully",
        data={"version": "2.0", "components": ["ai", "memory", "token_management"]},
        importance=7
    )
    
    # Test AI logging with token monitoring
    ai_logger.logger.info("AI system ready")
    
    # Simulate multiple AI operations
    ai_operations = [
        {
            "operation": "puzzle_analysis",
            "prompt": "Analyze the 3x3 grid puzzle with numbers 1-9 and identify patterns",
            "response": "Pattern identified: The puzzle follows Sudoku rules with additional constraints",
            "model": "llama3.2",
            "context": "grid_analysis"
        },
        {
            "operation": "hypothesis_generation",
            "prompt": "Generate mathematical hypotheses for solving the affine transformation puzzle",
            "response": "Hypothesis 1: Linear transformation; Hypothesis 2: Modular arithmetic; Hypothesis 3: Matrix operations",
            "model": "llama3.2",
            "context": "mathematical_reasoning"
        },
        {
            "operation": "solution_verification",
            "prompt": "Verify if the proposed solution satisfies all puzzle constraints",
            "response": "Solution verified: All constraints satisfied, puzzle solved successfully",
            "model": "llama3.2",
            "context": "verification"
        }
    ]
    
    total_tokens_used = 0
    for op in ai_operations:
        ai_logger.log_ai_operation(
            operation=op["operation"],
            prompt=op["prompt"],
            response=op["response"],
            model_name=op["model"],
            context_type=op["context"]
        )
        
        # Count tokens for summary
        prompt_tokens = get_token_manager().count_tokens(op["prompt"])
        response_tokens = get_token_manager().count_tokens(op["response"])
        total_tokens_used += prompt_tokens + response_tokens
    
    # Test context optimization logging
    ai_logger.log_context_optimization(
        original_size=2000,
        optimized_size=1200,
        context_type="puzzle_state",
        method="intelligent_truncation"
    )
    
    # Get summaries
    system_summary = system_logger.get_token_usage_summary(1)
    ai_summary = ai_logger.get_token_usage_summary(1)
    
    print(f"  System token usage: {system_summary.get('total_tokens', 0)} tokens")
    print(f"  AI token usage: {ai_summary.get('total_tokens', 0)} tokens")
    print(f"  Total tokens used in test: {total_tokens_used}")
    
    return total_tokens_used

def test_log_maintenance():
    """Test log maintenance and cleanup"""
    print("🧹 Testing log maintenance...")
    
    log_manager = get_log_manager()
    
    # Test cleanup of old files
    print("  Testing cleanup...")
    log_manager.cleanup_old_logs(days_old=0)  # Clean up immediately for testing
    
    # Check remaining files
    remaining_logs = list(Path(".").glob("*.log"))
    remaining_compressed = list(Path(".").glob("*.gz"))
    remaining_archives = list(Path("archives").glob("logs_archive_*")) if Path("archives").exists() else []
    
    print(f"  Remaining log files: {len(remaining_logs)}")
    print(f"  Remaining compressed files: {len(remaining_compressed)}")
    print(f"  Remaining archives: {len(remaining_archives)}")
    
    return len(remaining_logs) + len(remaining_compressed) + len(remaining_archives)

def test_performance_and_stress():
    """Test performance under stress conditions"""
    print("⚡ Testing performance under stress...")
    
    logger = create_integrated_logger("stress_test", logging.INFO)
    
    # Generate many log entries
    start_time = time.time()
    log_count = 1000
    
    for i in range(log_count):
        if i % 100 == 0:
            logger.logger.info(f"Stress test progress: {i}/{log_count}")
        
        # Mix of different log types
        if i % 3 == 0:
            logger.log_ai_operation(
                operation=f"stress_operation_{i}",
                prompt=f"Stress test prompt {i} with some content to analyze",
                response=f"Stress test response {i} with analysis results",
                model_name="stress-model",
                context_type="stress_test"
            )
        elif i % 5 == 0:
            logger.log_system_event(
                event_type="stress_event",
                description=f"Stress test event {i}",
                data={"iteration": i, "timestamp": datetime.now().isoformat()},
                importance=5
            )
        else:
            logger.logger.debug(f"Debug message {i}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"  Generated {log_count} log entries in {duration:.2f} seconds")
    print(f"  Performance: {log_count/duration:.1f} logs/second")
    
    # Get token usage summary
    token_summary = logger.get_token_usage_summary(1)
    print(f"  Token operations: {token_summary.get('total_operations', 0)}")
    print(f"  Total tokens: {token_summary.get('total_tokens', 0)}")
    
    return duration

def cleanup_test_files():
    """Clean up test files"""
    print("🧹 Cleaning up test files...")
    
    # Remove test files
    test_patterns = [
        "test_*.log",
        "test_*.log.gz",
        "intelligence_report_*.json",
        "intelligence_report_*.json.gz",
    ]
    
    removed_count = 0
    for pattern in test_patterns:
        for file_path in Path(".").glob(pattern):
            if file_path.is_file():
                file_path.unlink()
                removed_count += 1
    
    # Remove test directory
    test_dir = Path("test_logs")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        removed_count += 1
    
    # Remove archives
    archive_dir = Path("archives")
    if archive_dir.exists():
        shutil.rmtree(archive_dir)
        removed_count += 1
    
    print(f"  Removed {removed_count} test files/directories")

def main():
    """Run comprehensive log management tests"""
    print("🚀 Starting Log Management System Tests")
    print("=" * 60)
    
    try:
        # Create test data
        create_test_logs()
        
        # Test token monitoring
        token_report = test_token_monitoring()
        
        # Test compression and archiving
        compressed_count = test_compression_and_archiving()
        
        # Test database logging
        db_log_count = test_database_logging()
        
        # Test integrated logging
        total_tokens = test_integrated_logging()
        
        # Test maintenance
        remaining_files = test_log_maintenance()
        
        # Test performance
        stress_duration = test_performance_and_stress()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Token monitoring: {token_report.get('total_operations', 0)} operations, {token_report.get('total_tokens', 0)} tokens")
        print(f"✅ Compression: {compressed_count} files compressed")
        print(f"✅ Database logging: {db_log_count} logs stored in database")
        print(f"✅ Integrated logging: {total_tokens} tokens tracked")
        print(f"✅ Maintenance: {remaining_files} files remaining after cleanup")
        print(f"✅ Performance: {stress_duration:.2f}s for stress test")
        
        # Test results
        all_tests_passed = (
            token_report.get('total_operations', 0) > 0 and
            compressed_count > 0 and
            db_log_count > 0 and
            total_tokens > 0 and
            stress_duration < 30  # Should complete within 30 seconds
        )
        
        if all_tests_passed:
            print("\n🎉 ALL TESTS PASSED! Log management system is working correctly.")
        else:
            print("\n⚠️  Some tests may have issues. Check the output above.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always clean up
        cleanup_test_files()
        print("\n🧹 Cleanup complete.")

if __name__ == "__main__":
    main()
