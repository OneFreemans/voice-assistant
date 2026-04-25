from functions import (
    my_timer, time_kem, run_program, prank, what_weather, currency,
    what_dey, calculation_materials, open_website, search_yandex,
    print_heart, run_timer
)
from vk_functions import last_message, answer_last_message, messenger
from voice import say_text, process_result_and_restart
import config
import sys
import threading
import speech_recognition as sr
from time import sleep
from utils.logger import logger
from smart_home import control_device
from typing import Callable


#-------команды(триггер: (функция, кол-во мин арг., нужен ли отдельный поток)------
# исключения для мин. арг.: -1 вся строка без триггера; -2 вся строка включая триггер.
COMMANDS = {
    "таймер": (my_timer, 2, True),
    "сколько время": (time_kem, 0, False),
    "запусти": (run_program, 1, False),
    "расскажи анекдот": (prank, 0, False),
    "погода": (what_weather, 0, False),
    "курс": (currency, 1, False),
    "какой сегодня день": (what_dey, 0, False),
    "рассчитай": (calculation_materials, 1, False),
    "открой": (open_website, 1, False),
    "яндекс": (search_yandex, -1, False),
    "отправь сообщение": (messenger, -1, False),
    "последнее сообщение": (last_message, 0, False),
    "ответь на сообщение": (answer_last_message, -1, False),
    "сердце": (print_heart, 2, False),
    "включи": (control_device, -2, False),
    "выключи": (control_device, -2, False),
}


#-----------------------------------------tk-------------------------------------
_status_callback = None

def set_status_callback(callback: Callable[[int], None]) -> None:
    """
        Устанавливает функцию обратного вызова для изменения статуса голосового режима.

        Args:
            callback: Функция, принимающая один аргумент (int: 0 или 1) и возвращающая None.
        """
    global _status_callback
    _status_callback = callback


# -------------------начинаем прослушивание, определение команды-----------------
def listen_for_command() -> None:
    """
    Основная функция прослушивания команд.

    Слушает микрофон, распознаёт речь и проверяет команду активации "Олег".
    При успешной активации вызывает listen_for_command_after_activation().
    """
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        try:
            logger.info("Ожидаю команду 'Олег'...")
            audio = r.listen(source, timeout=2, phrase_time_limit=3)
            text = r.recognize_google(audio, language="ru-RU")
            logger.debug(f"Распознано: {text}")

            if text == "Олег стоп":
                say_text("Пока")
                sys.exit(0)

            elif config.match_activation_command(text, config.OLEG_COMMANDS):
                if _status_callback is not None:
                    _status_callback(1)
                return listen_for_command_after_activation()
            else:
                return None

        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None
        except Exception as e:
            logger.error(f"Ошибка распознавания: {e}")
            return None


def listen_for_command_after_activation() -> None:
    """
    Прослушивает команды после активации "Олег".

    Обрабатывает команды через универсальный парсер по словарю COMMANDS.
    Передаёт требуемые аргументы в функции.
    """
    with sr.Microphone() as source:
        r = sr.Recognizer()
        try:
            logger.info("Ожидаю команду...")
            if _status_callback is not None:
                _status_callback(2)
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language="ru-RU").lower()
            logger.info(f"Команда: {text}")

            if "стоп" in text:
                say_text("До скорых встреч!")
                sys.exit(0)

            # Поиск наиболее длинного совпадающего триггера
            matched_trigger = None
            for trigger in sorted(COMMANDS.keys(), key=len, reverse=True):  # сначала длинные
                if text.startswith(trigger + " ") or text == trigger:
                    matched_trigger = trigger
                    break

            if not matched_trigger:
                say_text(f"Я не знаю команду - {text}")
                return

            func, min_args, need_timer = COMMANDS[matched_trigger]

            # Удаляем триггер из текста
            args_part = text[len(matched_trigger):].strip()

            # Разбиваем на аргументы
            args = args_part.split()

            # Проверяем минимальное количество аргументов
            if min_args > 0 and len(args) < min_args:
                say_text(f"Команда '{matched_trigger}' требует минимум {min_args} аргументов.")
                return

            if min_args == 0:
                result = func()

            elif min_args == -2:
                result = func(matched_trigger, args_part)

            elif min_args == -1:
                result = func(args_part)

            elif min_args == 1:
                result = func(args[0])

            elif min_args == 2:
                result = func(args[0], args[1])

            else:
                result = func()

            process_result_and_restart(result)

            # Запуск таймера в отдельном потоке
            if need_timer and result and "таймер запущен" in result:
                timer_thread = threading.Thread(
                    target=run_timer,
                    args=(args[0], args[1])
                )
                timer_thread.daemon = True
                timer_thread.start()

        except Exception as e:
            print(f"Ошибка: {e}")


#---------------ТОЛЬКО ДЛЯ PYTEST(запуск с test_oleg.py - pytest)------------------------
def process_command_text(text: str) -> str: #FIXME обновить под новый process_command_text
    """
    Обрабатывает текст команды и возвращает результат.
    Скопировано из listen_for_command_after_activation, но без микрофона и озвучивания.
    """
    text_lower = text.lower()
    text_split = text_lower.split(" ")

    # ========== СПЕЦОБРАБОТКА ==========
    if "стоп" in text_lower:
        say_text("До скорых встреч!")
        sys.exit(0)

    # Управление устройствами
    if text_split[0] in ["включи", "выключи"] and len(text_split) > 1:
        return text

    # Отправка сообщения ВК
    if text_lower.startswith("отправь сообщение"):
        return text

    # Ответ на последнее сообщение ВК
    if text_lower.startswith("ответь на сообщение"):
        return text

    # Последнее сообщение ВК
    if text_lower == "последнее сообщение":
        return text

    # ========== КОМАНДЫ С ПРОБЕЛАМИ (без аргументов) ==========
    if text_lower in COMMANDS:
        # Для теста просто возвращаем текст команды
        return text

    # ========== ОБЫЧНЫЕ КОМАНДЫ С АРГУМЕНТАМИ ==========
    trigger = text_split[0]
    if trigger in COMMANDS:
        func, min_args, need_timer = COMMANDS[trigger]
        if len(text_split) > min_args:
            if min_args == 1:
                return text_split[1]
            elif min_args == 2:
                return " ".join(text_split[1:3])
            else:
                return text  # для теста возвращаем текст, а не вызов функции

    return f"Я не знаю команду - {text_lower}"


if __name__ == "__main__":
    logger.info("Запуск голосового ассистента")
    logger.info("Для активации скажите 'Олег'")
    logger.info("Начинаю прослушивание через...")
    sleep(1)
    for i in range(3, 0, -1):
        print(i, end="")
        sleep(1)
        if i == 1:
            print("\nГоворите!")

    while True:
        listen_for_command()
        sleep(0.1)