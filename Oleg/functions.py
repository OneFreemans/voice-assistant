import time, requests, subprocess, webbrowser, random, config
import speech_recognition as sr
from utils.anecdote import an
from utils.formatters import mesh, rub, cop, min as format_min
import datetime as dt
from utils.logger import logger


# ------------------------------------таймер-------------------------------------
def my_timer(time_timer: str, format_timer: str) -> str:
    """
    Создаёт сообщение о запуске таймера.

    Args:
        time_timer: Количество единиц времени (строка).
        format_timer: Единица измерения ("минут", "часов".).

    Returns:
        Строка с сообщением о запуске таймера.
    """

    formatted_min = format_min(time_timer)

    if format_timer in config.MINUTE_FORMATS:
        seconds = int(time_timer) * 60
        return f"таймер запущен на {time_timer} {formatted_min}. Таймер завершится через {seconds} секунд"

    if format_timer in config.HOUR_FORMATS:
        seconds = int(time_timer) * 60 * 60
        return f"таймер запущен на {time_timer} {format_timer}. Таймер завершится через {seconds} секунд"

    return f"Неизвестный формат времени: {format_timer}"


def run_timer(time_timer: str, format_timer: str) -> None:
    """
    Запускает таймер в отдельном потоке и выводит сообщение о завершении.

    Args:
        time_timer: Количество единиц времени (строка).
        format_timer: Единица измерения ("минут", "часов".).
    """
    if format_timer in config.MINUTE_FORMATS:
        time.sleep(int(time_timer) * 60)

    elif format_timer in config.HOUR_FORMATS:
        time.sleep(int(time_timer) * 60 * 60)

    print("Время вышло! Время вышло! Время вышло!")
    logger.info("Таймер завершён")


# --------------------------открывает ссылку в браузере--------------------------
def open_website(website: str) -> str:
    """
        Открывает указанный сайт в браузере.

        Args:
            website: Ключ сайта из словаря config.WEBSITES.

        Returns:
            Сообщение об успехе или ошибке.
        """
    if website in config.WEBSITES:
        webbrowser.open_new_tab(f'https://{config.WEBSITES[website]}')
        return f"{website} открыт"

    return f"Сайт '{website}' не найден в базе данных"


# --------------------ищет пользовательский запрос в яндексе---------------------
def search_yandex(user_request: str) -> str:
    """
    Открывает указанный запрос в браузере (поисковик Яндекс).

    Args:
        user_request: Запрос пользователя.

    Returns:
        Сообщение об успешном открытии или "Запрос не указан".
    """
    parts = user_request.split(" ")
    if len(parts) > 1:
        query = "+".join(parts)
        webbrowser.open_new_tab(f'https://yandex.ru/search/?text={query}&lr=64')
        return f"Открываю ссылку по вашему запросу: {query.replace('+', ' ')}"

    return "Запрос не указан"


# ---------------------------расчет материал для стяжки--------------------------
def calculation_materials(mat: str) -> str:
    """
    Рассчитывает материалы для стяжки или наливного пола через голосовой ввод.

    Args:
        mat: Тип материала ("стяжку" или "наливной").

    Returns:
        Строка с результатом расчёта или сообщение об ошибке.
    """
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        print("Скажите: N квадратов(площадь), X сантиметров(толщина)")
        print("Пример: 40 квадратов 5 сантиметров")
        for i in range(3, 0, -1):
            print(i, end="")
            time.sleep(1)
            if i == 1:
                print("\nГоворите!")
        try:
            audio = r.listen(source, phrase_time_limit=3)
            text = r.recognize_google(audio, language="ru-RU").lower()
            parts = text.split(" ")
            logger.debug(f"Распознано для расчёта: {text} -> {parts}")

            if len(parts) < 3:
                return "Не удалось распознать данные. Попробуйте ещё раз."

            try:
                area = float(parts[0])
                thickness = float(parts[2])
            except ValueError:
                return "Не удалось распознать числа. Попробуйте ещё раз."

            if area <= 0 or thickness <= 0:
                return "Площадь и слой должны быть положительными числами."

            if mat not in config.MATERIALS:
                return f"Материал '{mat}' не найден в базе данных"

            kf, kgm, price_m, price_r = map(int, config.MATERIALS[mat].split(", "))
            total_kg = thickness * kf * area / kgm
            total_cost_material = total_kg * price_m
            total_cost_work = area * price_r

            bags = mesh(int(total_kg))
            cost_material = rub(int(total_cost_material))
            cost_work = rub(int(total_cost_work))

            return (f"Понадобится {int(total_kg)} {bags}, на материал уйдёт {int(total_cost_material)} "
                    f"{cost_material}, за работу возьмите {int(total_cost_work)} {cost_work}")

        except sr.UnknownValueError:
            return "Не удалось распознать речь. Попробуйте ещё раз."
        except sr.RequestError:
            return "Ошибка сервиса распознавания речи."


# ----------------------------------текущий день---------------------------------
def what_dey(city: int = config.UTC_OFFSET) -> str:
    """
    Возвращает текущую дату с учётом часового пояса.

    Args:
        city: Часовой сдвиг в часах относительно UTC (по умолчанию из config.UTC_OFFSET).

    Returns:
        Строка с датой в формате "сегодня ДД.ММ.ГГГГ".
    """
    city_day = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=city)
    return city_day.strftime("сегодня %d.%m.%Y")


# -------------------------------курс волют к рублю------------------------------
def currency(currency_name: str) -> str:
    """
    Возвращает текущий курс доллара или евро в рублях.

    Args:
        currency_name: "доллар" или "евро".

    Returns:
        Строка с курсом валюты или сообщение об ошибке.
    """
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        response.raise_for_status()
        data = response.json()
        usd_rate = data["Valute"]["USD"]["Value"]
        eur_rate = data["Valute"]["EUR"]["Value"]
    except requests.RequestException:
        return "Не удалось получить курс с сайта ЦБ"

    if currency_name in ("доллара", "доллар"):
        course = usd_rate
        rubles = int(course)
        cents = round((course - rubles) * 100)
        return f"курс доллара {rubles} {rub(rubles)} {cents} {cop(cents)}"

    if currency_name == "евро":
        course = eur_rate
        rubles = int(course)
        cents = round((course - rubles) * 100)
        return f"курс евро {rubles} {rub(rubles)} {cents} {cop(cents)}"

    return "Не удалось обработать запрос на курс валют"


# -----------------------------------анекдоты------------------------------------
def prank() -> str:
    """
    Возвращает случайный анекдот из anecdote.an.

    Returns:
        Строка с анекдотом или сообщение, что список пуст.
    """
    return random.choice(an) if an else "Список анекдотов пуст."


# ------------------------------запуск программ на пк----------------------------
def run_program(name_prog: str) -> str:
    """
    Запускает программу из config.PROGRAMS.

    Args:
        name_prog: Ключ из config.PROGRAMS.

    Returns:
        Сообщение об успешном запуске, ошибке или отсутствии программы.
    """
    if name_prog not in config.PROGRAMS:
        return f"Программа {name_prog} не найдена в базе данных"

    try:
        process = subprocess.Popen(config.PROGRAMS[name_prog])
        # poll() возвращает None, если процесс ещё работает
        if process.poll() is None:
            return f"Программа {name_prog} запускается"

        else:
            return f"Не удалось запустить {name_prog}"
    except FileNotFoundError:
        return f"Файл программы {name_prog} не найден"
    except PermissionError:
        return f"Нет прав на запуск {name_prog}"
    except Exception as e:
        return f"Ошибка при запуске {name_prog}: {str(e)}"


# ---------------------------------текущие время---------------------------------
def time_kem() -> str:
    """
    Возвращает текущее время в формате ЧЧ:ММ:СС.
    """
    return time.strftime("%H:%M:%S", time.localtime())


# ---------------------------------погода сегодня--------------------------------
def what_weather(city: str = config.DEFAULT_CITY) -> str:
    """
    Получает погоду для указанного города с сервиса wttr.in.

    Args:
        city: Название города (по умолчанию из config.DEFAULT_CITY).

    Returns:
        Строка с погодой или сообщение об ошибке.
    """
    url = f'http://wttr.in/{city}'

    weather_parameters = {
        'format': '%l: %t %C',  # город: температура + описание
        'M': '',                # скорость ветра в м/с
        'lang': 'ru',           # язык — русский
        'A': ''                 # отключить цвета (ANSI escape codes)
    }

    try:
        response = requests.get(url, params=weather_parameters, timeout=5)
        response.raise_for_status()
        response.encoding = 'utf-8'
        text = response.text.strip()
        return text
    except requests.ConnectionError:
        return "Сетевая ошибка"
    except requests.Timeout:
        return "Таймаут при запросе погоды"
    except requests.RequestException as e:
        return f"Ошибка при получении погоды: {str(e)}"


# ---------------------------Рисует сердце--------------------
def print_heart(amount: str, color: str) -> str:
    """
    Рисует указанное количество сердечек заданного цвета в консоли.

    Args:
        amount: Количество сердечек (строка, преобразуется в int).
        color: Название цвета (например, "красное", "синее").

    Returns:
        Строка с отчётом о количестве нарисованных сердец.
    """

    COLORS = {
        "красное": "\033[91m",
        "зелёное": "\033[92m",
        "жёлтое": "\033[93m",
        "синее": "\033[94m",
        "фиолетовое": "\033[95m",
        "голубое": "\033[96m",
        "белое": "\033[97m",
        "reset": "\033[0m"
    }

    try:
        count = int(amount)
    except ValueError:
        return f"Ошибка: '{amount}' не является числом"

    color_code = COLORS.get(color.lower(), COLORS["белое"])

    for _ in range(count):
        heart_lines = [
            "  ♥ ♥   ♥ ♥  ",
            " ♥   ♥ ♥   ♥ ",
            " ♥    ♥    ♥ ",
            "  ♥       ♥  ",
            "   ♥     ♥   ",
            "    ♥   ♥    ",
            "     ♥ ♥     ",
            "      ♥      "
        ]
        for line in heart_lines:
            print(f"{color_code}{line}{COLORS['reset']}")
        print()

    return f"Нарисовано {count} сердец цветом {color}"