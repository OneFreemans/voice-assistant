from functions import *


# ---------------------------Функции озвучивания и перезапуска--------------------
def say_text(text, wait=True):
    """Озвучивает текст (с пересозданием движка для надежности)"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'irina' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(text)
        if wait:
            engine.runAndWait()
    except Exception as e:
        print(f"Ошибка озвучки: {e}")


def process_result_and_restart(result, success_message=None):
    """Обрабатывает результат функции: выводит, озвучивает"""
    if isinstance(result, dict):
        if 'error' in result:
            say_text(result['error'])
            print(result['error'])
        elif 'message' in result:
            say_text(result['message'])
            print(result['message'])
        elif 'data' in result:
            say_text(result['data'])
            print(result['data'])
    elif result:
        say_text(result)
        print(result)

    if success_message:
        say_text(success_message)
        print(success_message)


# -------------------начинаем прослушивание, определение команды-----------------
def listen_for_command():
    """Основная функция прослушивания команд"""
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        try:
            print("Ожидаю команду 'Джарвис'...")                              # noqa
            audio = r.listen(source, timeout=2, phrase_time_limit=3)
            text = r.recognize_google(audio, language="ru-RU")
            print(f"Распознано: {text}")

            if text == "Джарвис стоп":                                         # noqa
                say_text("Пока")
                sys.exit(0)

            elif text in config.JARVIS_COMMANDS:
                # say_text("Слушаю")
                return listen_for_command_after_activation()
            else:
                return None

        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None
        except Exception as e:
            print(f"Ошибка: {e}")
            return None


def listen_for_command_after_activation():
    """Прослушивание команд после активации"""
    with sr.Microphone() as source:
        r = sr.Recognizer()

        try:
            print("Ожидаю команду...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language="ru-RU").lower()
            text_split = text.split(" ")
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
                if trigger == text_split[0] and len(text_split) > min_args:
                    func = globals()[func_name]

                    if min_args == 1:
                        result = func(text_split[1])
                    elif min_args == 2:
                        result = func(text_split[1], text_split[2])
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
            print("Не распознано")
        except sr.RequestError:
            print("Ошибка сервиса распознавания речи")
        except sr.WaitTimeoutError:
            pass
        except Exception as e:
            print(f"Произошла неизвестная ошибка: {e}")


# Запуск программы
if __name__ == "__main__":
    print("hello world! \nДля активации скажите 'Джарвис'")                # noqa
    print("Начинаю прослушивание через...")
    sleep(1)
    for i in range(3, 0, -1):
        print(i, end="")
        sleep(1)
        if i == 1:
            print("\nГоворите!")

    while True:
        listen_for_command()
        sleep(0.1)