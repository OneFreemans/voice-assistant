import speech_recognition as sr
from Oleg.core.voice import say_text
from Oleg.utils.logger import logger
import requests
from Oleg.secrets import DEEPSEEK_API_KEY


def ask_ai(question: str, history: list) -> tuple[str, list]:
    """
    Отправляет вопрос в DeepSeek API с учётом истории диалога.

    Args:
        question: Текст вопроса пользователя.
        history: Список предыдущих сообщений в формате:
                 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

    Returns:
        Кортеж (ответ_ассистента, обновлённая_история).
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [
        {
            "role": "system",
            "content": (
                "Ты — голосовой ассистент по имени Олег. "
                "Отвечай кратко, чётко, без воды. Маты разрешены, говори по-русски."
            ),
        }
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    payload = {"model": "deepseek-chat", "messages": messages, "temperature": 0.8}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"]

        new_history = history.copy()
        new_history.append({"role": "user", "content": question})
        new_history.append({"role": "assistant", "content": answer})

        # Храним последние 10 сообщений
        if len(new_history) > 10:
            new_history = new_history[-10:]

        return answer, new_history

    except Exception as e:
        logger.error(f"DeepSeek API error: {e}")
        return "Извини, не могу ответить сейчас.", history


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
                    say_text(answer)

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                say_text("Не расслышал, повторите.")
            except sr.RequestError as e:
                logger.error(f"Ошибка распознавания речи: {e}")
                say_text("Ошибка соединения с сервером распознавания.")

    logger.info("AI режим завершён")
