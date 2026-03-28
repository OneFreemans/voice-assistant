import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# -------------------------------------------------------------------
# Глобальная переменная для хранения функции обратного вызова (callback),
# которая будет отправлять сообщения лога в графический интерфейс (GUI).
# -------------------------------------------------------------------
_gui_callback = None


# -------------------------------------------------------------------
# Функция для регистрации callback'а из GUI.
# GUI вызывает её один раз при запуске, передавая свою функцию on_log.
# -------------------------------------------------------------------
def set_gui_callback(callback):
    global _gui_callback
    _gui_callback = callback


# -------------------------------------------------------------------
# Кастомный обработчик логов для отправки сообщений в GUI.
# -------------------------------------------------------------------
class GuiHandler(logging.Handler):
    def emit(self, record):
        # Проверяем, что callback существует и является вызываемым объектом
        if _gui_callback is not None and callable(_gui_callback):
            msg = self.format(record)
            _gui_callback(msg)


# -------------------------------------------------------------------
# Основная функция настройки логгера.
# name: имя логгера (по умолчанию "oleg")
# Возвращает настроенный объект logger.
# -------------------------------------------------------------------
def setup_logger(name: str = "oleg") -> logging.Logger:
    # Получаем логгер с указанным именем
    logger = logging.getLogger(name)

    # Если у логгера уже есть обработчики, не добавляем повторно
    if logger.handlers:
        return logger

    # Устанавливаем минимальный уровень логирования (DEBUG — всё)
    logger.setLevel(logging.DEBUG)

    # Формат сообщения: дата время | уровень | текст
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # --- Хендлер для консоли (вывод на экран) ---
    # Показываем только INFO и выше, чтобы не засорять консоль отладкой
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    # --- Хендлер для файла (сохранение всех логов) ---
    # Папка logs создаётся в корне проекта (на уровень выше utils)
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)  # создаём папку, если её нет

    # RotatingFileHandler: при достижении 5 МБ создаёт новый файл, хранит 3 копии
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "oleg.log"),
        maxBytes=5 * 1024 * 1024,  # 5 мегабайт
        backupCount=3,  # хранить 3 старых файла
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # пишем ВСЁ (и отладку, и ошибки)
    file_handler.setFormatter(formatter)

    # --- Хендлер для GUI (отправка логов в интерфейс) ---
    gui_handler = GuiHandler()
    gui_handler.setLevel(logging.DEBUG)  # отправляем всё
    gui_handler.setFormatter(formatter)

    # Добавляем все хендлеры в логгер
    logger.addHandler(console)
    logger.addHandler(file_handler)
    logger.addHandler(gui_handler)

    return logger


# -------------------------------------------------------------------
# Создаём и экспортируем глобальный логгер.
# В других модулях используем: from utils.logger import logger
# -------------------------------------------------------------------
logger = setup_logger()