"""
Production Logging Configuration
================================

Centralized logging configuration for TauTranslator.
"""

import logging
import logging.handlers
import os
import json
from datetime import datetime
from pathlib import Path


class ProductionLogConfig:
    """Production-ready logging configuration."""
    
    # Log levels
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # Default configuration
    DEFAULT_LEVEL = "INFO"
    LOG_DIR = Path("logs")
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5
    
    # Log format
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s"
    
    @classmethod
    def setup_logging(cls, 
                     app_name: str = "tau_translator",
                     level: str = None,
                     log_to_file: bool = True,
                     log_to_console: bool = True,
                     json_format: bool = False):
        """
        Setup production logging configuration.
        
        Args:
            app_name: Application name for log files
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Enable file logging
            log_to_console: Enable console logging
            json_format: Use JSON format for logs
        """
        # Create log directory
        if log_to_file:
            cls.LOG_DIR.mkdir(exist_ok=True)
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(cls.LOG_LEVELS.get(level or cls.DEFAULT_LEVEL, logging.INFO))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(root_logger.level)
            
            if json_format:
                console_handler.setFormatter(JsonFormatter())
            else:
                console_handler.setFormatter(logging.Formatter(cls.DEFAULT_FORMAT))
            
            root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_to_file:
            log_file = cls.LOG_DIR / f"{app_name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=cls.MAX_BYTES,
                backupCount=cls.BACKUP_COUNT
            )
            file_handler.setLevel(root_logger.level)
            
            if json_format:
                file_handler.setFormatter(JsonFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(cls.DETAILED_FORMAT))
            
            root_logger.addHandler(file_handler)
            
            # Error log file
            error_file = cls.LOG_DIR / f"{app_name}_error.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_file,
                maxBytes=cls.MAX_BYTES,
                backupCount=cls.BACKUP_COUNT
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(logging.Formatter(cls.DETAILED_FORMAT))
            root_logger.addHandler(error_handler)
        
        # Suppress noisy libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("transformers").setLevel(logging.WARNING)
        
        return root_logger


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", 
                          "funcName", "levelname", "levelno", "lineno", 
                          "module", "msecs", "pathname", "process", 
                          "processName", "relativeCreated", "thread", 
                          "threadName", "exc_info", "exc_text", "stack_info"]:
                log_data[key] = value
        
        return json.dumps(log_data)


class LoggerFactory:
    """Factory for creating configured loggers."""
    
    @staticmethod
    def get_logger(name: str, level: str = None) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: Logger name (usually __name__)
            level: Optional specific log level for this logger
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(name)
        
        if level:
            logger.setLevel(ProductionLogConfig.LOG_LEVELS.get(level, logging.INFO))
        
        return logger


# Production logging utilities
def log_function_call(func):
    """Decorator to log function calls."""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {e}", exc_info=True)
            raise
    
    return wrapper


def log_performance(func):
    """Decorator to log function performance."""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {elapsed_time:.3f} seconds")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {elapsed_time:.3f} seconds: {e}")
            raise
    
    return wrapper


# Initialize logging on import
if __name__ != "__main__":
    # Setup default logging when imported
    ProductionLogConfig.setup_logging(
        level=os.getenv("TAU_LOG_LEVEL", "INFO"),
        json_format=os.getenv("TAU_LOG_JSON", "false").lower() == "true"
    )