from functions import (
    time_kem, what_dey, what_weather, currency, prank,
    my_timer, print_heart, search_yandex,
    run_program, open_website
)
import pytest
from unittest.mock import patch, MagicMock
from main import process_command_text
from vk_functions import last_message
from smart_home import control_device
from utils.formatters import mesh, rub, cop, min as format_min
from Oleg.utils.anecdote import an
import config


def test_time_kem():
    """Тест функции времени"""
    result = time_kem()
    assert len(result) == 8, f"Неправильная длина строки: {len(result)} вместо 8"


def test_what_dey():
    """Тест функции даты"""
    result = what_dey()
    assert len(result) == 18, f"what_dey() -> Неправильная длина строки: {len(result)} вместо 18"


def test_currency():
    """Тест функции курса валют"""

    # Тест для доллара
    result_usd = currency("доллар")
    assert result_usd != "Не удалось получить курс с сайта ЦБ", "Не удалось получить курс доллара"
    assert "курс доллара" in result_usd, "В ответе нет 'курс доллара'"
    assert "руб" in result_usd or "рублей" in result_usd, "В ответе нет рублей"

    # Тест для евро
    result_eur = currency("евро")
    assert result_eur != "Не удалось получить курс с сайта ЦБ", "Не удалось получить курс евро"
    assert "курс евро" in result_eur, "В ответе нет 'курс евро'"
    assert "руб" in result_eur or "рублей" in result_eur, "В ответе нет рублей"

    # Тест для неизвестной валюты
    result_unknown = currency("фунт")
    assert result_unknown == "Не удалось обработать запрос на курс валют", "Должна быть ошибка для неизвестной валюты"


def test_what_weather():
    result = what_weather()
    assert isinstance(result, str)
    assert len(result) > 0
    assert "ошибка" not in result.lower()


def test_prank():
    """Тест функции анекдотов"""
    result = prank()
    assert result in an, "Анекдот не из списка"
    assert len(result) > 0, "Анекдот пустой"


@pytest.mark.parametrize("func, value, expected", [
    # mesh
    (mesh, 1, "мешок"),
    (mesh, 2, "мешка"),
    (mesh, 5, "мешков"),
    (mesh, 11, "мешков"),
    (mesh, 21, "мешок"),
    (mesh, 24, "мешка"),
    # rub
    (rub, 1, "рубль"),
    (rub, 2, "рубля"),
    (rub, 5, "рублей"),
    (rub, 11, "рублей"),
    (rub, 21, "рубль"),
    (rub, 24, "рубля"),
    # cop
    (cop, 1, "копейка"),
    (cop, 2, "копейки"),
    (cop, 5, "копеек"),
    (cop, 11, "копеек"),
    (cop, 21, "копейка"),
    (cop, 24, "копейки"),
    # min
    (format_min, 1, "минута"),
    (format_min, 2, "минуты"),
    (format_min, 5, "минут"),
    (format_min, 11, "минут"),
    (format_min, 21, "минута"),
    (format_min, 24, "минуты"),
])
def test_formatters_param(func, value, expected):
    """Параметризованный тест для всех склонений"""
    assert func(value) == expected, f"{func.__name__}({value}) должно быть '{expected}'"


def test_my_timer():
    """Тест функции таймера"""
    result_min = my_timer("5", "минут")
    assert "5" in result_min
    assert "минут" in result_min

    result_hour = my_timer("2", "часа")
    assert "2" in result_hour
    assert "часа" in result_hour

    result_unknown = my_timer("3", "секунды")
    assert "Неизвестный формат" in result_unknown


def test_print_heart():
    """Тест функции рисования сердечек (только возврат. Печать не проверяется)"""
    result = print_heart("3", "красное")
    assert "Нарисовано 3 сердец" in result
    assert "красное" in result


def test_open_website():
    """Тест открытия сайта (проверяем только возврат)"""
    result_ok = open_website("вк")
    assert "открыт" in result_ok

    result_bad = open_website("несуществующийсайт")
    assert "не найден" in result_bad


def test_search_yandex():
    """Тест поиска в Яндексе (проверяем только возврат)"""
    result_ok = search_yandex("яндекс погода")
    assert "Открываю ссылку" in result_ok

    result_bad = search_yandex("яндекс")
    assert "Запрос не указан" in result_bad


def test_run_program():
    """Тест запуска программы с моком subprocess.Popen"""
    # Мокаем subprocess.Popen
    with patch('functions.subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # процесс запущен
        mock_popen.return_value = mock_process

        result = run_program("steam")
        assert "запускается" in result
        mock_popen.assert_called_once_with(config.PROGRAMS["steam"])

        # Тест для несуществующей программы
        result = run_program("неизвестная_программа")
        assert "не найдена" in result


def test_control_device():
    """Тест управления устройством с моком"""
    with patch('smart_home.control_yandex_device') as mock_yandex:
        mock_yandex.return_value = "Устройство включено"

        # Патчим словарь YANDEX_DEVICE_IDS в config
        with patch.dict(config.YANDEX_DEVICE_IDS, {"свет": "test_id"}):
            result = control_device("включи", "свет")
            assert "Устройство" in result
            mock_yandex.assert_called_once_with("test_id", "on")


def test_last_message():
    """Тест last_message с моком"""
    mock_vk = MagicMock()
    mock_vk.messages.getConversations.return_value = {
        'count': 1,
        'items': [{
            'last_message': {
                'from_id': 123,
                'text': 'Тестовое сообщение'
            }
        }]
    }
    mock_vk.users.get.return_value = [{
        'first_name': 'Тест',
        'last_name': 'Тестов'
    }]

    with patch('vk_functions.vk', mock_vk):
        result = last_message()
        assert 'Тест Тестов' in result
        assert 'Тестовое сообщение' in result


@pytest.mark.parametrize("command, expected", [
    # ===== КОМАНДЫ С return trigger, args_part (min_args = -2) =====
    ("включи свет в комнате", ('включи', 'свет в комнате')),
    ("выключи свет", ('выключи', 'свет')),

    # ===== КОМАНДЫ С return args_part (min_args = -1) =====
    ("отправь сообщение Тест Тестов привет", "Тест Тестов привет"),
    ("ответь на сообщение спасибо", "спасибо"),

    # ===== КОМАНДЫ С return args[0] (min_args = 1) =====
    ("открой вк", "вк"),
    ("запусти steam", "steam"),
    ("курс доллар", "доллар"),
    ("курс евро", "евро"),
    ("удали заметку 5", "5"),

    # ===== КОМАНДЫ С return (args[0], args[1]) (min_args = 2) =====
    ("таймер 5 минут", ('5', 'минут')),
    ("сердце 5 красное", ('5', 'красное')),

    # ===== КОМАНДЫ С return "нет аргументов" (min_args = 0) =====
    ("последнее сообщение", "нет аргументов"),
    ("сколько время", "нет аргументов"),
    ("расскажи анекдот", "нет аргументов"),
    ("погода", "нет аргументов"),
    ("какой сегодня день", "нет аргументов"),
    ("заметки", "нет аргументов"),
    ("удали все заметки", "нет аргументов"),
    ("стоп", "До скорых встреч!"),
])
def test_process_command_text(command, expected):
    """Параметризованный тест для проверки маршрутизации команд"""
    assert process_command_text(command) == expected


@pytest.mark.parametrize("command, expected_substring", [
    ("что-то непонятное", "Я не знаю команду"),
    ("таймер", "требует минимум 2 аргументов"),
    ("сердце 5", "требует минимум 2 аргументов"),
])
def test_process_command_text_errors(command, expected_substring):
    """Параметризованный тест для проверки ошибок маршрутизации команд"""
    assert expected_substring in process_command_text(command)