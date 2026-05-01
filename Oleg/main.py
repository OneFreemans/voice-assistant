from Oleg.functions import (
    my_timer,
    time_kem,
    run_program,
    prank,
    what_weather,
    currency,
    what_dey,
    calculation_materials,
    open_website,
    search_yandex,
    print_heart,
    run_timer,
)
from Oleg.vk_functions import last_message, answer_last_message, messenger
from Oleg.voice import say_text, process_result_and_restart
from Oleg import config
import sys
import threading
import speech_recognition as sr
from time import sleep
from Oleg.utils.logger import logger
from Oleg.smart_home import control_device
from typing import Callable
from Oleg.notes import add_note, list_notes, delete_note, clear_notes
from Oleg.utils.command_parser import parse_command

# -------команды(триггер: (функция, кол-во мин арг., нужен ли отдельный поток)------
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
    "добавь заметку": (add_note, -1, False),
    "заметки": (list_notes, 0, False),
    "удали заметку": (delete_note, 1, False),
    "удали все заметки": (clear_notes, 0, False),
}


# -----------------------------------------tk-------------------------------------
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
                    _status_callback(1)  # noqa
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

            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language="ru-RU").lower()
            logger.info(f"Команда: {text}")

            if "стоп" in text:
                say_text("До скорых встреч!")
                sys.exit(0)

            # Парсит полученный текст
            trigger, args_part, args = parse_command(text, COMMANDS)

            if not trigger:
                say_text(f"Я не знаю команду - {text}")
                return

            func, min_args, need_timer = COMMANDS[trigger]

            # Проверяем минимальное количество аргументов
            if min_args > 0 and len(args) < min_args:
                say_text(f"Команда '{trigger}' требует минимум {min_args} аргументов.")
                return

            if min_args == 0:
                result = func()

            elif min_args == -2:
                result = func(trigger, args_part)

            elif min_args == -1:
                result = func(args_part)

            elif min_args == 1:
                result = func(args[0])

            elif min_args == 2:
                result = func(args[0], args[1])

            else:
                result = func()

            process_result_and_restart(result)

            if _status_callback is not None:
                _status_callback(2)  # noqa

            # Запуск таймера в отдельном потоке
            if need_timer and result and "таймер запущен" in result:
                timer_thread = threading.Thread(
                    target=run_timer, args=(args[0], args[1])
                )
                timer_thread.daemon = True
                timer_thread.start()

        except Exception as e:
            print(f"Ошибка: {e}")


# ---------------ТОЛЬКО ДЛЯ PYTEST(запуск с test_oleg.py - pytest)------------------------
def process_command_text(text: str):
    """
    Обрабатывает текст команды и возвращает результат.
    Скопировано из listen_for_command_after_activation, но без микрофона и озвучивания.
    """
    if "стоп" in text:
        return "До скорых встреч!"

    # Парсит полученный текст
    trigger, args_part, args = parse_command(text, COMMANDS)

    if not trigger:
        return f"Я не знаю команду - {text}"

    func, min_args, need_timer = COMMANDS[trigger]

    # Проверяем минимальное количество аргументов
    if min_args > 0 and len(args) < min_args:
        return f"Команда '{trigger}' требует минимум {min_args} аргументов."

    if min_args == 0:
        return "нет аргументов"

    elif min_args == -2:
        return trigger, args_part

    elif min_args == -1:
        return args_part

    elif min_args == 1:
        return args[0]

    elif min_args == 2:
        return args[0], args[1]

    else:
        return "не правильное кол-во аргументов"


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
