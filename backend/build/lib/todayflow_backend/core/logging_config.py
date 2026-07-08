"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path

from todayflow_backend.core.config import settings


def setup_logging() -> None:
    """
    Configure centralized logging for the application.
    
    Sets up:
    - Console handler with appropriate format
    - File handler (optional, for production)
    - Log levels based on environment
    """
    # Determine log level based on environment
    log_level = logging.DEBUG if settings.environment == "development" else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    logging.getLogger("todayflow_backend").setLevel(log_level)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

