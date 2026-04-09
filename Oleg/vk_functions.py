import vk_api
from utils.transformers import transform_data_vk
from secrets import VK_TOKEN, MY_USER_ID


session = vk_api.VkApi(token=VK_TOKEN)
vk = session.get_api()


# ---------------------------Ответ на последние сообщение----------------------------
def answer_last_message(message_text: str) -> str:
    """
    Пишет сообщение последнему человеку в диалогах.

    Args:
        message_text: Текст сообщения.

    Returns:
        Текст об успешной отправки сообщения или ошибку.
    """
    dialogs = vk.messages.getConversations(count=1)

    if dialogs and dialogs['count'] > 0:
        last_dialog = dialogs['items'][0]
        last_message_vk = last_dialog['last_message']
        user_id = last_message_vk['from_id']
        # Убираем команду "ответь на сообщение" из текста
        message = message_text.replace("ответь на сообщение ", "")
        session.method("messages.send", {"user_id": user_id, "random_id": 0, "message": message})

        user_info = vk.users.get(user_ids=user_id, fields='first_name, last_name')
        first_name = user_info[0]['first_name']
        last_name = user_info[0]['last_name']

        return f"Доставлено {first_name} {last_name}. Отправленное сообщение: {message}"

    return "Не удалось получить диалоги или диалоги пусты"


# ----------------------------Последние сообщение ВК--------------------------------
def last_message() -> str:
    """
    Читает последнее сообщение ВК.

    Returns:
        Текст последнего сообщения или ошибку.
    """
    dialogs = vk.messages.getConversations(count=1)

    if dialogs and dialogs['count'] > 0:
        last_dialog = dialogs['items'][0]
        last_messages = last_dialog['last_message']
        user_id = last_messages['from_id']
        message = last_messages["text"]

        user_info = vk.users.get(user_ids=user_id, fields='first_name, last_name')
        first_name = user_info[0]['first_name']
        last_name = user_info[0]['last_name']

        return f"Сообщение от {first_name} {last_name}: {message}"

    return "Диалоги не найдены"


# -----------------------------отправка сообщений вк-----------------------------
def messenger(name_and_messages: str) -> str:
    """
    Ищет пользователя в друзьях и отправляет сообщение.

    Args:
        name_and_messages: Имя фамилия и текст сообщения.

    Returns:
        Текст успешного отправления сообщения или ошибку.
    """
    name_and_message = name_and_messages.replace("отправь сообщение ", "")
    words = name_and_message.split(" ")

    if len(words) < 3:
        return "Недостаточно данных. Формат: отправь сообщение [Имя Фамилия] [текст сообщения]"

    name = words[0] + " " + words[1]
    message = name_and_message.replace(name, "", 1).strip()

    my_friends = session.method("friends.get", {"user_id": MY_USER_ID, "fields": 0})
    name_id = transform_data_vk(my_friends)

    if name in name_id.keys():
        session.method("messages.send", {"user_id": name_id[name], "random_id": 0, "message": message})
        return f"Сообщение отправлено {name}: {message}"

    return f"Пользователь {name} не найден в друзьях"