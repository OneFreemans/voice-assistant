import pyttsx3
import threading
import time
from Oleg.utils.logger import logger
from typing import Optional, Union
import speech_recognition as sr


# ---------------------------Функции озвучивания и перезапуска ядра--------------------
def say_text(text: str, wait: bool = True) -> None:
    """
    Озвучивает текст (создаёт новый движок каждый раз для надёжности)

    Args:
        text: Текст для озвучивания
        wait: Если True — озвучивает синхронно, если False — в отдельном потоке.

    Returns:
        None
    """

    def _speak():
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 240)  # Скорость речи
            engine.setProperty("volume", 1.0)  # Громкость

            # Ищем голос Irina
            for voice in engine.getProperty("voices"):
                if "irina" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            logger.error(f"Ошибка озвучки: {e}")

    if wait:
        _speak()

    else:
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()


def process_result_and_restart(
    result: Union[str, dict, None], success_message: Optional[str] = None
) -> None:
    """Обрабатывает результат функции: выводит, озвучивает

    Args:
        result: Результат функции
        success_message: Сообщение, которое будет выводиться, если функция успешно выполнена

    Returns:
        None
    """
    if isinstance(result, dict):
        if "error" in result:
            say_text(result["error"])
            logger.error(result["error"])

        elif "message" in result:
            say_text(result["message"])
            logger.info(result["message"])

        elif "data" in result:
            say_text(result["data"])
            logger.info(result["data"])

    elif result:
        say_text(result)
        logger.info(result)

    if success_message:
        say_text(success_message)
        logger.info(success_message)


# ---------------------------Голосовой ввод для расчета материалов--------------------
def get_text_from_microphone() -> str | None:
    """
    Захватывает речь через микрофон и возвращает распознанный текст.
    Выводит подсказку для пользователя, ждёт 3 секунды, затем слушает микрофон.

    Returns:
        str | None: Распознанный текст в нижнем регистре или None при ошибке.
    """
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        print("Скажите: N квадратов(площадь), X сантиметров(толщина)")
        print("Пример: 40 квадратов 5 сантиметров")
        for i in range(3, 0, -1):
            print(i, end="")
            time.sleep(1)
            if i == 1:
                print("\nГоворите!")

        try:
            audio = r.listen(source, phrase_time_limit=3)
            text = r.recognize_google(audio, language="ru-RU").lower()
            logger.debug(f"Распознано: {text}")
            return text
        except sr.UnknownValueError:
            logger.warning("Речь не распознана")
            return None
        except sr.RequestError as e:
            logger.error(f"Ошибка сервиса распознавания: {e}")
            return None
