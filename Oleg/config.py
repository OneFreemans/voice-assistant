# Команды для активации
JARVIS_COMMANDS = ["Jarvis", "Джа", "Джарв", "Джарви", "Джарвис", "Джарвиз", "jarvi", "Джаред", "shareit", "Чарльз", "джар"]


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
    "стяжку": "19, 25, 318, 600",
    "наливной": "21, 25, 432, 250",
}


# Курсы валют
CURRENCY_NAMES = {
    "доллара": "USD",
    "евро": "EUR",
}


WORD_CURRENCY = {
    "доллар": "USD",
    "евро": "EUR",
}


# Список команд для обработки
# Формат: (триггер, минимальное кол-во аргументов, имя функции, нужен ли отдельный поток)
COMMANDS = [
    ("стоп", 0, "stop_handler", False),
    ("таймер", 2, "my_timer", True),
    ("сколько время", 0, "time_kem", False),
    ("запусти", 1, "run_program", False),
    ("расскажи анекдот", 0, "prank", False),
    ("погода", 0, "what_weather", False),
    ("курс", 0, "currency", False),
    ("какой сегодня день", 0, "what_dey", False),
    ("рассчитай", 1, "calculation_materials", False),
    ("открой", 1, "open_website", False),
    ("яндекс", 0, "search_yandex", False),
    ("отправь сообщение", 0, "messenger", False),
    ("последнее сообщение", 0, "last_message", False),
    ("ответь на сообщение", 0, "answer_last_message", False),
    ("сердце", 2, "print_heart", False),
]
