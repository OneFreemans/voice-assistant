from collections import defaultdict


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
        print(f"Ошибка при обработке данных: {e}")
        return {}