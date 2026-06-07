"""
Логирование с поддержкой JSON формата
Логи идут в консоль с красивым форматом для разработки
В production могут отправляться в LangFuse
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    jsonlogger = None


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Настроить логгер с форматом для разработки
    
    Args:
        name: имя логгера (обычно __name__)
        level: уровень логирования (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        logging.Logger: настроенный логгер
        
    Example:
        logger = setup_logger(__name__)
        logger.info("Сообщение")
    """
    
    logger = logging.getLogger(name)
    
    # Не добавляем handlers если они уже есть
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Консоль логгер (красивый формат для разработки)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Форматер с эмодзи для наглядности
    console_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Глобальный логгер приложения
# Используется во всём приложении для логирования
app_logger = setup_logger("autoparts", level=logging.INFO)
