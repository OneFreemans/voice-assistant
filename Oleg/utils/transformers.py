from collections import defaultdict
from utils.logger import logger


# -----------------------------Обработка словаря от ВК-----------------------------
def transform_data_vk(data):
    try:
        data_items = data.get('items', [])

        if not data_items:
            return {}

        result = defaultdict(list)

        for item in data_items:
            full_name = f"{item['first_name']} {item['last_name']}"
            full_name = full_name.lower()
            result[full_name].append(item['id'])

        return dict(result)

    except (KeyError, TypeError) as e:
        logger.error(f"Ошибка при обработке данных VK: {e}")
        return {}