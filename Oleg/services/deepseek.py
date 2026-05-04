from Oleg.secrets import DEEPSEEK_API_KEY
from Oleg.utils.logger import logger
import requests


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
                "Отвечай кратко, чётко, без воды. Маты разрешены, говори по-русски. "
                "НЕ ИСПОЛЬЗУЙ markdown-разметку (звёздочки, подчёркивания, решётки). "
                "Твой текст будет прочитан вслух, поэтому пиши чистыми словами."
            ),
        }
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    payload = {"model": "deepseek-chat", "messages": messages, "temperature": 0.7}

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
