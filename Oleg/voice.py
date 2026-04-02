import pyttsx3
import threading
from utils.logger import logger


# ---------------------------Функции озвучивания и перезапуска--------------------
def say_text(text, wait=True):
    """Озвучивает текст (создаёт новый движок каждый раз для надёжности)"""
    def _speak():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 240)  # Скорость речи
            engine.setProperty('volume', 1.0)  # Громкость

            # Ищем голос Irina
            for voice in engine.getProperty('voices'):
                if 'irina' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
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


def process_result_and_restart(result, success_message=None):
    """Обрабатывает результат функции: выводит, озвучивает"""
    if isinstance(result, dict):
        if 'error' in result:
            say_text(result['error'])
            logger.error(result['error'])
        elif 'message' in result:
            say_text(result['message'])
            logger.info(result['message'])
        elif 'data' in result:
            say_text(result['data'])
            logger.info(result['data'])
    elif result:
        say_text(result)
        logger.info(result)

    if success_message:
        say_text(success_message)
        logger.info(success_message)
