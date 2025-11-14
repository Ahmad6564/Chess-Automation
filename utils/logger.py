"""
Logging module for unified logging and error tracking.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(name: str = 'chess_agent',
                log_file: Optional[str] = None,
                level: int = logging.INFO,
                console: bool = True) -> logging.Logger:
    """
    Set up a logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file (if None, creates default in logs/)
        level: Logging level
        console: Whether to also log to console
    
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    if log_file is None:
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f'chess_agent_{timestamp}.log'
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized - Log file: {log_file}")
    
    return logger


def get_logger(name: str = 'chess_agent') -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


class LogContext:
    """Context manager for logging specific operations."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            operation: Name of the operation
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Start the operation."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the operation."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation} ({duration:.2f}s)")
        else:
            self.logger.error(f"Failed: {self.operation} ({duration:.2f}s) - {exc_val}")
        
        return False  # Don't suppress exceptions


def log_move(logger: logging.Logger, 
            move: str, 
            fen_before: str, 
            fen_after: str,
            thinking_time: float):
    """
    Log a chess move with context.
    
    Args:
        logger: Logger instance
        move: Move in UCI format
        fen_before: FEN before move
        fen_after: FEN after move
        thinking_time: Time taken to calculate move
    """
    logger.info(
        f"Move: {move} | "
        f"Time: {thinking_time:.2f}s | "
        f"Before: {fen_before[:30]}... | "
        f"After: {fen_after[:30]}..."
    )


def log_vision_result(logger: logging.Logger,
                     pieces_detected: int,
                     confidence: Optional[float] = None,
                     processing_time: Optional[float] = None):
    """
    Log vision processing results.
    
    Args:
        logger: Logger instance
        pieces_detected: Number of pieces detected
        confidence: Detection confidence score
        processing_time: Time taken to process
    """
    msg = f"Vision: Detected {pieces_detected} pieces"
    
    if confidence is not None:
        msg += f" | Confidence: {confidence:.2%}"
    
    if processing_time is not None:
        msg += f" | Time: {processing_time:.2f}s"
    
    logger.info(msg)


def log_error(logger: logging.Logger,
             error: Exception,
             context: str = ""):
    """
    Log an error with context.
    
    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context about the error
    """
    msg = f"Error"
    if context:
        msg += f" in {context}"
    msg += f": {type(error).__name__} - {str(error)}"
    
    logger.error(msg, exc_info=True)


if __name__ == "__main__":
    # Test logger
    print("Testing logger...")
    
    logger = setup_logger('test_logger')
    
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test log context
    with LogContext(logger, "Test operation"):
        import time
        time.sleep(1)
        logger.info("Operation in progress...")
    
    print("Logger test complete. Check logs/ directory.")
