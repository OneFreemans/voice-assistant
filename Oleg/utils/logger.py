import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "oleg") -> logging.Logger:
    """Настраивает логгер с консольным и файловым выводом"""
    logger = logging.getLogger(name)
    
    # Избегаем дублирования при повторном вызове
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Формат: время - уровень - сообщение
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Консоль (только INFO и выше)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    
    # Файл (все уровни, макс 5MB, 3 файла ротация)
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "oleg.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger


# Глобальный логгер
logger = setup_logger()
