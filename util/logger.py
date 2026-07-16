import logging
import os
import sys

class Logger:
    """Unified logging interface for SPACE_BOUND_AI."""
    
    def __init__(self, name="SPACE_BOUND_AI", level=None):
        """Initialize logger with consistent formatting.
        
        Args:
            name: Logger name (typically module name)
            level: Log level (defaults to INFO, can be overridden by LOG_LEVEL env var)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Clear any existing handlers
        self.logger.handlers = []
        
        # Determine log level from environment or parameter
        if level is None:
            level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
            level = getattr(logging, level_str, logging.INFO)
        
        self.logger.setLevel(level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.propagate = False
    
    def debug(self, msg, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)
