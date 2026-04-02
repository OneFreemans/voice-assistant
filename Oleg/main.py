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


#-------команды(тригер: (функция, кол-во мин арг., нужен ли отдельный поток)------
COMMANDS = {
    "таймер": (my_timer, 2, True),
    "сколько время": (time_kem, 0, False),
    "запусти": (run_program, 1, False),
    "расскажи анекдот": (prank, 0, False),
    "погода": (what_weather, 0, False),
    "курс": (currency, 0, False),
    "какой сегодня день": (what_dey, 0, False),
    "рассчитай": (calculation_materials, 1, False),
    "открой": (open_website, 1, False),
    "яндекс": (search_yandex, 0, False),
    "отправь сообщение": (messenger, 0, False),
    "последнее сообщение": (last_message, 0, False),
    "ответь на сообщение": (answer_last_message, 0, False),
    "сердце": (print_heart, 2, False),
    "включи": (control_device, 1, False),
    "выключи": (control_device, 1, False),
}


#-----------------------------------------tk-------------------------------------
_status_callback = None

def set_status_callback(callback):
    global _status_callback
    _status_callback = callback


# -------------------начинаем прослушивание, определение команды-----------------
def listen_for_command():
    """Основная функция прослушивания команд"""
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        try:
            logger.info("Ожидаю команду 'Олег'...")
            audio = r.listen(source, timeout=2, phrase_time_limit=3)
            text = r.recognize_google(audio, language="ru-RU")
            logger.debug(f"Распознано: {text}")

            if text == "Олег стоп":                                         # noqa
                say_text("Пока")
                sys.exit(0)

            elif config.match_activation_command(text, config.OLEG_COMMANDS):
                if _status_callback is not None:
                    _status_callback(1)  # 1 — активирован, жду команду   # noqa
                # say_text("Слушаю")
                return listen_for_command_after_activation()
            else:
                return None

        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None
        except Exception as e:
            logger.error(f"Ошибка распознавания: {e}")
            return None


def listen_for_command_after_activation():
    with sr.Microphone() as source:
        r = sr.Recognizer()
        try:
            print("Ожидаю команду...")
            if _status_callback is not None:
                _status_callback(2)
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language="ru-RU").lower()
            text_split = text.split(" ")
            print(f"Команда: {text}")

            # Спецобработка стоп
            if "стоп" in text:
                say_text("До скорых встреч!")
                sys.exit(0)

            # Проверяем команды из словаря
            trigger = text_split[0]

            # Спецобработка для управления устройствами (включи/выключи)
            if trigger in ["включи", "выключи"] and len(text_split) > 1:
                device = " ".join(text_split[1:])
                action = trigger
                result = control_device(device, action)
                process_result_and_restart(result)
                return

            if trigger in COMMANDS:
                func, min_args, need_timer = COMMANDS[trigger]
                if len(text_split) > min_args:
                    if min_args == 0:
                        result = func()
                    elif min_args == 1:
                        result = func(text_split[1])
                    elif min_args == 2:
                        result = func(text_split[1], text_split[2])
                    else:
                        result = func()

                    process_result_and_restart(result)

                    if need_timer and result and "таймер запущен" in result:
                        timer_thread = threading.Thread(
                            target=run_timer,
                            args=(text_split[1], text_split[2])
                        )
                        timer_thread.daemon = True
                        timer_thread.start()
                    return

            # Команды с пробелами (например "сколько время")
            if text in COMMANDS:
                func, min_args, need_timer = COMMANDS[text]
                result = func()
                process_result_and_restart(result)
                return

            # Если ничего не нашли
            say_text(f"Я не знаю команду - {text}")

        except Exception as e:
            print(f"Ошибка: {e}")


# Запуск программы
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

    logger.info("Ожидаю команды...")

    while True:
        listen_for_command()
        sleep(0.1)