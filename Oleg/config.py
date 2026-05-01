from Oleg.utils.fuzzy import match_activation_command, FUZZY_THRESHOLD  # noqa

# Яндекс Умный дом
# структура - "команда после триггера включи или выключи": "ID устройства"
YANDEX_DEVICE_IDS = {
    "свет в комнате": "3193e021-ce11-41f6-aa10-779a688ace42",  # свет в комнате
    "кулер": "01bf4270-e182-4725-bf47-16c0b7811585",  # розетка кулера
    "свет в кухни": "fb256f9a-304f-4848-b0ab-e045239759db",  # свет на кухне
    "свет в ванной": "187d7c73-d101-4f09-a533-9a23bab2ca37",  # свет в ванне
    "свет в коридоре": "5abee79a-f38f-4fbf-a599-3815fab9895e",  # свет в коридоре
    "гирлянда": "d4485a12-d62e-4056-809c-7cdc86a91723",  # гирлянда
    "проектор": "d36ecbe7-1fdb-44cb-b953-ed9ddd28e2d3",  # проектор
}


# Команды для активации
OLEG_COMMANDS = ["Олег", "Олежа", "Олежка"]


# Типы команд
REQUEST_O = ["рассчитай", "подсчитай", "посчитай", "прочитай", "рассчитать"]
CURRENCY = ["курс", "доллар", "евро"]
REQUEST_YANDEX = ["яндекс", "индекс"]


# Форматы времени
MINUTE_FORMATS = ["минут", "минуты", "минуту", "минута"]
HOUR_FORMATS = ["часов", "часа", "час"]
UTC_OFFSET = 7
DEFAULT_CITY = "кемерово"


# База данных программ
PROGRAMS = {
    "steam": "D:\\Steam\\steam.exe",
    "discord": "C:\\Users\\OneFr\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe",
    "браузер": "C:\\Users\\OneFr\\AppData\\Local\\Yandex\\YandexBrowser\\Application\\browser.exe",
    "телеграм": "E:\\Prog\\Telegram Desktop\\Telegram.exe",
    "telegram": "E:\\Prog\\Telegram Desktop\\Telegram.exe",
}


# Сайты
WEBSITES = {
    "вк": "vk.com",
    "vk": "vk.com",
    "телеграм": "web.telegram.org/k/",
    "telegram": "web.telegram.org/k/",
    "ютуб": "www.youtube.com",
    "youtube": "www.youtube.com",
    "2гис": "2gis.ru/kemerovo",
    "авито": "www.avito.ru",
    "твич": "www.twitch.tv/",
    "twitch": "www.twitch.tv/",
    "гит": "https://github.com/OneFreemans/voice-assistant",
    "git": "https://github.com/OneFreemans/voice-assistant",
    "музыку": "https://music.yandex.ru/",
}


# Материалы для стяжки
MATERIALS = {
    # "материал": "кэф, вес мешка, цена мешка, цена работы за м*2"
    "стяжку": "19, 25, 424, 900",
    "наливной": "21, 25, 744, 350",
}
