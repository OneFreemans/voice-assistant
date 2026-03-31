import config
from secrets import YANDEX_TOKEN
from models.yandex_smart_home import YandexSmartHome

# Создаём клиент один раз
yh = YandexSmartHome(YANDEX_TOKEN)


def control_yandex_device(device_id, action):
    """Отправляет команду в Яндекс.Умный дом"""
    status, response = yh.control_device(device_id, action)
    if status == 200:
        return f"✅ Устройство {action == 'on' and 'включено' or 'выключено'}"
    else:
        return f"❌ Ошибка: {response}"


def control_device(device_name, action):
    """
    device_name: "свет", "розетка" и т.д. (ключ из config.YANDEX_DEVICE_IDS)
    action: "включи" или "выключи"
    """
    device_id = config.YANDEX_DEVICE_IDS.get(device_name)
    if not device_id:
        return f"❌ Устройство '{device_name}' не найдено в конфиге"

    cmd = "on" if action == "включи" else "off"
    return control_yandex_device(device_id, cmd)