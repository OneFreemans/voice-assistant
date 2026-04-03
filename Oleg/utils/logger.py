import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Callable, Optional


_gui_callback: Optional[Callable[[str], None]] = None

def set_gui_callback(callback: Callable[[str], None]) -> None:
    """
    Устанавливает функцию обратного вызова для отправки логов в GUI.

    Args:
        callback: Функция, принимающая строку (сообщение лога) и возвращающая None.
    """
    global _gui_callback
    _gui_callback = callback


# Кастомный обработчик логов для отправки сообщений в GUI.
class GuiHandler(logging.Handler):
    """
    Кастомный обработчик логов для отправки сообщений в графический интерфейс.
    """
    def emit(self, record: logging.LogRecord) -> None:
        """
        Отправляет отформатированное сообщение лога в GUI через колбэк.

        Args:
            record: Объект записи лога (LogRecord).
        """
        # Проверяем, что callback существует и является вызываемым объектом
        if _gui_callback is not None and callable(_gui_callback):
            msg = self.format(record)
            _gui_callback(msg)


# Основная функция настройки логгера.
def setup_logger(name: str = "oleg") -> logging.Logger:
    """
    Настраивает и возвращает логгер с выводом в консоль, файл и GUI.

    Args:
        name: Имя логгера (по умолчанию "oleg").

    Returns:
        Настроенный объект logging.Logger.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Консольный хендлер (только INFO и выше)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    # Файловый хендлер (ротация 5 МБ, 3 файла)
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

    # GUI-хендлер (отправка в интерфейс)
    gui_handler = GuiHandler()
    gui_handler.setLevel(logging.DEBUG)
    gui_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.addHandler(gui_handler)

    return logger


# В других модулях используем: from utils.logger import logger
logger = setup_logger()