import logging
import sys
from datetime import datetime

def setup_logging():
    """Configure logging with datetime stamps for all outputs"""
    
    # Create custom formatter with datetime
    class DateTimeFormatter(logging.Formatter):
        def format(self, record):
            # Add timestamp to the record
            record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return super().format(record)
    
    # Define log format with timestamp
    log_format = '[%(timestamp)s] %(levelname)s - %(name)s - %(message)s'
    
    # Create formatter
    formatter = DateTimeFormatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    loggers = [
        'app.services.sync_service',
        'app.services.scheduler',
        'app.api.main',
        'app.services.ai_bot',
        'app.api.chat',
        'mcp_server',
        'uvicorn',
        'fastapi'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        # Propagate to root logger which has our formatter
        logger.propagate = True