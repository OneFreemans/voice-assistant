import speech_recognition as sr
from Oleg.core.voice import say_text
from Oleg.utils.logger import logger
from Oleg.services.deepseek import ask_ai


def ai_chat_mode() -> None:
    """
    Запускает режим общения с ИИ.

    Особенности:
        - Работает в отдельном цикле, не мешая основной активации по ключевому слову.
        - Сохраняет контекст диалога (последние 5 обменов репликами).
        - Выход из режима по фразам: «закончить сессию» или «выход».
    """
    say_text("Режим собеседника включён.")
    logger.info("AI режим активирован")

    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        history = []

        while True:
            try:
                say_text("Слушаю...")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio, language="ru-RU").lower()
                logger.debug(f"AI режим: распознано: {text}")

                if "закончить сессию" in text or "выход" in text:
                    say_text("Завершаю режим собеседника.")
                    break

                if text:
                    answer, history = ask_ai(text, history)
                    print(answer)
                    say_text(answer)

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                say_text("Не расслышал, повторите.")
            except sr.RequestError as e:
                logger.error(f"Ошибка распознавания речи: {e}")
                say_text("Ошибка соединения с сервером распознавания.")

    logger.info("AI режим завершён")
