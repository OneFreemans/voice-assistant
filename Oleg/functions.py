import time, requests, subprocess, webbrowser, random, sys, threading, config # noqa
import speech_recognition as sr
from utils.anecdote import an
from utils.formatters import mesh, rub, cop, min
import datetime as dt
from time import sleep
from vk_functions import answer_last_message, last_message, messenger # noqa
from voice import say_text, process_result_and_restart # noqa


# ------------------------------------таймер-------------------------------------
def my_timer(time_timer, format_timer):
    for_m = min(time_timer)

    if format_timer in config.MINUTE_FORMATS:
        timer_seconds = int(time_timer) * 60
        return f"таймер запущен на {time_timer} {for_m}. Таймер завершится через {timer_seconds} секунд"

    elif format_timer in config.HOUR_FORMATS:
        timer_seconds = int(time_timer) * 60 * 60
        return f"таймер запущен на {time_timer} {format_timer}. Таймер завершится через {timer_seconds} секунд"

    return f"Неизвестный формат времени: {format_timer}"


def run_timer(time_timer, format_timer):
    """Запускает таймер в отдельном потоке"""

    if format_timer in config.MINUTE_FORMATS:
        sleep(int(time_timer) * 60)
    elif format_timer in config.HOUR_FORMATS:
        sleep(int(time_timer) * 60 * 60)

    say_text("Время вышло! Время вышло! Время вышло!")
    print("Время вышло! Время вышло! Время вышло!")


# --------------------------открывает ссылку в браузере--------------------------
def open_website(website):
    if website in config.WEBSITES:
        webbrowser.open_new_tab(f'https://{config.WEBSITES[website]}')
        return f"{website} открыт"

    return f"Сайт '{website}' не найден в базе данных"


# --------------------ищет пользовательский запрос в яндексе---------------------
def search_yandex(user_request):
    user_request = user_request.split(" ")
    if len(user_request) > 1:
        del user_request[0]
        user_request = "+".join(user_request)
        webbrowser.open_new_tab(f'https://yandex.ru/search/?text={user_request}&lr=64')
        return f"Открываю ссылку по вашему запросу: {user_request.replace('+', ' ')}"

    return "Запрос не указан"


# ---------------------------расчет материал для стяжки--------------------------
def calculation_materials(mat):
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        say_text(f"скажите н квадратов и следом слой икс сантиметров")

        try:
            audio = r.listen(source, phrase_time_limit=3)
            text = r.recognize_google(audio, language="ru-RU")
            text = text.lower()
            text_split = text.split(" ")
            print(text, text_split)

            if len(text_split) >= 3:
                m2 = float(text_split[0])
                sm = float(text_split[2])

                if mat in config.MATERIALS:
                    kf = int((config.MATERIALS[mat]).split(", ")[0])
                    kgm = int((config.MATERIALS[mat]).split(", ")[1])
                    price_m = int((config.MATERIALS[mat]).split(", ")[2])
                    price_r = int((config.MATERIALS[mat]).split(", ")[3])

                    result_m = sm * kf * m2 / kgm
                    result_mr = result_m * price_m
                    result_rr = m2 * price_r

                    for_m = mesh(int(result_m))
                    for_rm = rub(int(result_mr))
                    for_rr = rub(int(result_rr))

                    return (f"Понадобится {int(result_m)} {for_m}, на материал уйдёт {int(result_mr)} "
                            f"{for_rm}, за работу возьмите {int(result_rr)} {for_rr}")
                else:
                    return f"Материал '{mat}' не найден в базе данных"
            else:
                return "Не удалось распознать данные. Попробуйте еще раз"

        except sr.UnknownValueError:
            return "Не удалось распознать речь. Попробуйте еще раз"
        except sr.RequestError:
            return "Ошибка сервиса распознавания речи"


# ----------------------------------текущий день---------------------------------
def what_dey(city=config.UTC_OFFSET):
    city_day = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=city)
    return city_day.strftime("сегодня %d.%m.%Y")


# -------------------------------курс волют к рублю------------------------------
def currency(currency_name):
    try:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")
        data = response.json()
        usd_rate = data["Valute"]["USD"]["Value"]
        eur_rate = data["Valute"]["EUR"]["Value"]
    except:                                                                          # noqa
        return "Не удалось получить курс с сайта ЦБ"

    if currency_name == "доллара" or currency_name == "доллар":
        course = usd_rate
        rubles = int(course)
        cents = round((course - rubles) * 100)
        return f"курс доллара {rubles} {rub(rubles)} {cents} {cop(cents)}"

    elif currency_name == "евро":
        course = eur_rate
        rubles = int(course)
        cents = round((course - rubles) * 100)
        return f"курс евро {rubles} {rub(rubles)} {cents} {cop(cents)}"

    return "Не удалось обработать запрос на курс валют"


# -----------------------------------анекдоты------------------------------------
def prank():
    an_it = len(an)
    number = random.randint(0, an_it - 1)
    return an[number]


# ------------------------------запуск программ на пк----------------------------
def run_program(name_prog):
    if name_prog in config.PROGRAMS:
        try:
            notepad = subprocess.Popen(config.PROGRAMS[name_prog])
            notepad.poll()

            if str(notepad.poll()) == "None":
                return f"Программа {name_prog} запускается"
            else:
                return f"Не удалось запустить {name_prog}"
        except Exception as e:
            return f"Ошибка при запуске {name_prog}: {str(e)}"

    return f"Программа {name_prog} не найдена в базе данных"


# ---------------------------------текущие время---------------------------------
def time_kem():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time


# ---------------------------------погода сегодня--------------------------------
def what_weather(city=config.DEFAULT_CITY):
    url = f'http://wttr.in/{city}'

    weather_parameters = {
        'format': 3,
        'M': '',  # скорость ветра в м/с
        'lang': 'ru',  # язык — русский
        'A': ''  # отключить цвета (ANSI escape codes)
    }

    try:
        response = requests.get(url, params=weather_parameters, timeout=5)
        response.raise_for_status()

        response.encoding = 'utf-8'

        text = response.text.strip()

        return text.replace('\n', '').replace('\r', '')

    except requests.ConnectionError:
        return "Сетевая ошибка"
    except requests.Timeout:
        return "Таймаут при запросе погоды"
    except Exception as e:
        return f"Ошибка при получении погоды: {str(e)}"


# ---------------------------Рисует сердце--------------------
def print_heart(amount, color):
    colors = {
        "красное": "\033[91m",
        "зелёное": "\033[92m",
        "жёлтое": "\033[93m",
        "синее": "\033[94m",
        "фиолетовое": "\033[95m",
        "голубое": "\033[96m",
        "белое": "\033[97m",
        "reset": "\033[0m"
    }

    color_code = colors.get(color.lower(), colors["белое"])

    # Рисуем каждое сердечко
    for _ in range(int(amount)):
        heart = [
            "  ♥ ♥   ♥ ♥  ",
            " ♥   ♥ ♥   ♥ ",
            " ♥    ♥    ♥ ",
            "  ♥       ♥  ",
            "   ♥     ♥   ",
            "    ♥   ♥    ",
            "     ♥ ♥     ",
            "      ♥      "
        ]

        # Выводим сердечко с цветом
        for line in heart:
            print(f"{color_code}{line}{colors['reset']}")
        print()  # пустая строка между сердечками

    return f"Нарисовано {amount} сердец цветом {color}"