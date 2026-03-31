from functions import *
from utils.logger import logger

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
    """Прослушивание команд после активации"""
    with sr.Microphone() as source:
        r = sr.Recognizer()

        try:
            logger.info("Ожидаю команду...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language="ru-RU").lower()
            text_split = text.split(" ")
            logger.debug(f"Команда: {text}")
            print(f"Команда: {text}")

            # Проверяем все команды из конфига
            for trigger, min_args, func_name, need_timer in config.COMMANDS:

                # Спецобработка для команды "стоп"
                if trigger == "стоп" and "стоп" in text:
                    say_text("До скорых встреч!")
                    sys.exit(0)

                # Обработка команд с пробелами (например "запусти стим")
                if " " in trigger and text == trigger:
                    func = globals()[func_name]
                    result = func()
                    process_result_and_restart(result)
                    return

                # Обработка команд с аргументами (например "таймер 5 минут")
                if trigger == text_split[0]:
                    func = globals()[func_name]

                    if min_args == 1:
                        result = func(text_split[1])
                    elif min_args == 2:
                        result = func(text_split[1], text_split[2])
                    elif min_args == 999:
                        result = func(" ".join(text_split[1:]), text_split[0])
                    else:
                        result = func()

                    process_result_and_restart(result)

                    # Если это таймер и он запустился
                    if need_timer and result and "таймер запущен" in result:
                        timer_thread = threading.Thread(
                            target=run_timer,
                            args=(text_split[1], text_split[2])
                        )
                        timer_thread.daemon = True
                        timer_thread.start()
                    return

            # Если ни одна команда не подошла
            say_text(f"Я не знаю команду - {text}")

        except sr.UnknownValueError:
            logger.debug("Не распознано")
        except sr.RequestError:
            logger.error("Ошибка сервиса распознавания речи")
        except sr.WaitTimeoutError:
            pass
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")
        finally:
            if _status_callback is not None:
                _status_callback(0)  # вернулся в режим ожидания   # noqa


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