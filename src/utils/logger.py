"""
Logging Setup für Trading Bot
"""
import logging
import colorlog
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "TradingBot",
    log_level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Richtet einen Logger mit Farb-Output und File-Logging ein
    
    Args:
        name: Name des Loggers
        log_level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Pfad zur Log-Datei (optional)
    
    Returns:
        Konfigurierter Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Verhindere doppelte Handler
    if logger.handlers:
        return logger
    
    # Console Handler mit Farben
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    console_format = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File Handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger
