#!/usr/bin/env python3
"""
Integration module for log management system with autonomous AI systems
Provides seamless integration between log management and existing systems
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

from log_management import get_log_manager, DatabaseLogHandler, LogConfig
from token_manager import get_token_manager

# Configure logging for this module
logger = logging.getLogger(__name__)

class IntegratedLogger:
    """Integrated logger that combines file logging, database storage, and token monitoring"""
    
    def __init__(self, name: str, log_level: int = logging.INFO, 
                 enable_db_logging: bool = True, enable_token_monitoring: bool = True):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.enable_db_logging = enable_db_logging
        self.enable_token_monitoring = enable_token_monitoring
        
        # Initialize log manager
        self.log_manager = get_log_manager(
            config=LogConfig(
                token_monitoring_enabled=enable_token_monitoring,
                max_tokens_per_hour=50000  # Conservative limit for AI operations
            )
        )
        
        # Setup handlers
        self._setup_handlers()
        
        logger.info(f"IntegratedLogger initialized for {name}")
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file = f"logs/{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Database handler for important logs
        if self.enable_db_logging:
            db_handler = DatabaseLogHandler(self.log_manager)
            db_handler.setLevel(logging.WARNING)  # Only store warnings and errors in DB
            self.logger.addHandler(db_handler)
    
    def log_ai_operation(self, operation: str, prompt: str, response: str = None, 
                        model_name: str = None, context_type: str = None, 
                        session_id: str = None, **kwargs):
        """Log AI operation with token monitoring"""
        # Log the operation
        self.logger.info(f"AI Operation: {operation}")
        
        if self.enable_token_monitoring:
            # Count tokens
            token_manager = get_token_manager()
            prompt_tokens = token_manager.count_tokens(prompt)
            response_tokens = token_manager.count_tokens(response) if response else 0
            
            # Track token usage
            self.log_manager.track_token_usage(
                operation=operation,
                prompt_tokens=prompt_tokens,
                response_tokens=response_tokens,
                model_name=model_name,
                context_type=context_type,
                session_id=session_id
            )
            
            # Log token usage
            self.logger.debug(f"Token usage for {operation}: {prompt_tokens} + {response_tokens} = {prompt_tokens + response_tokens}")
    
    def log_context_optimization(self, original_size: int, optimized_size: int, 
                               context_type: str, method: str = "truncation"):
        """Log context optimization events"""
        reduction_ratio = (original_size - optimized_size) / original_size if original_size > 0 else 0
        
        self.logger.info(f"Context optimization: {context_type} reduced from {original_size} to {optimized_size} tokens "
                        f"({reduction_ratio:.1%} reduction) using {method}")
        
        # Store optimization details in database
        self.log_manager.store_log_in_db(
            logging.LogRecord(
                name=self.name,
                level=logging.INFO,
                pathname="log_integration.py",
                lineno=1,
                msg=f"Context optimization: {context_type} optimized",
                args=(),
                exc_info=None
            ),
            extra_data={
                'optimization_type': 'context',
                'context_type': context_type,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'reduction_ratio': reduction_ratio,
                'method': method
            }
        )
    
    def log_compression_stats(self, file_path: str, original_size: int, 
                             compressed_size: int, method: str = "gzip"):
        """Log file compression statistics"""
        compression_ratio = compressed_size / original_size if original_size > 0 else 0
        
        self.logger.info(f"File compression: {file_path} compressed from {original_size} to {compressed_size} bytes "
                        f"({compression_ratio:.1%} ratio) using {method}")
    
    def log_system_event(self, event_type: str, description: str, 
                        data: Dict[str, Any] = None, importance: int = 5):
        """Log system events with structured data"""
        self.logger.log(
            level=self._importance_to_level(importance),
            msg=f"System Event: {event_type} - {description}"
        )
        
        # Store structured data in database for important events
        if importance >= 7:  # High importance events
            self.log_manager.store_log_in_db(
                logging.LogRecord(
                    name=self.name,
                    level=self._importance_to_level(importance),
                    pathname="log_integration.py",
                    lineno=1,
                    msg=f"System Event: {event_type}",
                    args=(),
                    exc_info=None
                ),
                extra_data={
                    'event_type': event_type,
                    'description': description,
                    'importance': importance,
                    'data': data
                }
            )
    
    def _importance_to_level(self, importance: int) -> int:
        """Convert importance score to logging level"""
        if importance >= 9:
            return logging.CRITICAL
        elif importance >= 7:
            return logging.ERROR
        elif importance >= 5:
            return logging.WARNING
        elif importance >= 3:
            return logging.INFO
        else:
            return logging.DEBUG
    
    def get_token_usage_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get token usage summary"""
        return self.log_manager.get_token_usage_report(hours)
    
    def get_recent_logs(self, level: str = None, limit: int = 50) -> list:
        """Get recent logs from database"""
        return self.log_manager.query_logs(
            level=level,
            logger_name=self.name,
            limit=limit
        )
    
    def perform_maintenance(self):
        """Trigger log maintenance tasks"""
        self.logger.info("Triggering log maintenance tasks")
        self.log_manager.compress_old_logs()
        self.log_manager.archive_old_logs()
        self.log_manager.cleanup_old_logs()

# Factory function to create integrated loggers
def create_integrated_logger(name: str, log_level: int = logging.INFO, 
                           enable_db_logging: bool = True, 
                           enable_token_monitoring: bool = True) -> IntegratedLogger:
    """Create an integrated logger instance"""
    return IntegratedLogger(
        name=name,
        log_level=log_level,
        enable_db_logging=enable_db_logging,
        enable_token_monitoring=enable_token_monitoring
    )

# Pre-configured loggers for different components
def get_system_logger() -> IntegratedLogger:
    """Get system-wide logger"""
    return create_integrated_logger("autonomous_system", logging.INFO)

def get_ai_logger() -> IntegratedLogger:
    """Get AI-specific logger with token monitoring"""
    return create_integrated_logger("ai_operations", logging.INFO, 
                                  enable_token_monitoring=True)

def get_memory_logger() -> IntegratedLogger:
    """Get memory system logger"""
    return create_integrated_logger("memory_system", logging.INFO)

def get_token_logger() -> IntegratedLogger:
    """Get token management logger"""
    return create_integrated_logger("token_management", logging.DEBUG, 
                                  enable_token_monitoring=True)

# Integration function to upgrade existing logging
def upgrade_system_logging():
    """Upgrade existing system to use integrated logging"""
    # Replace the default logging configuration
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Add integrated handler
    integrated_handler = DatabaseLogHandler(get_log_manager())
    integrated_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    root_logger.addHandler(integrated_handler)
    
    logger.info("System logging upgraded to integrated log management")

if __name__ == "__main__":
    # Test the integrated logging system
    print("🔧 Testing Integrated Logging System")
    print("=" * 50)
    
    # Create integrated loggers
    system_logger = get_system_logger()
    ai_logger = get_ai_logger()
    
    # Test basic logging
    system_logger.logger.info("System startup complete")
    
    # Test AI operation logging
    ai_logger.log_ai_operation(
        operation="hypothesis_generation",
        prompt="Generate mathematical hypothesis for puzzle solving",
        response="Hypothesis: The puzzle follows affine transformation pattern",
        model_name="llama3.2",
        context_type="mathematical_analysis"
    )
    
    # Test system event logging
    system_logger.log_system_event(
        event_type="strategy_execution",
        description="Successfully executed intelligent mathematical attack",
        data={"strategy": "intelligent_mathematical_attack", "success_rate": 0.85},
        importance=8
    )
    
    # Test token usage summary
    token_summary = ai_logger.get_token_usage_summary(1)
    print(f"Token usage summary: {token_summary}")
    
    print("✅ Integrated logging system tests complete!")
