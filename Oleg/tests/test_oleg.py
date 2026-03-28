import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Oleg.main import *


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
    result = currency("курс доллара")
    assert result != "Не удалось обработать запрос на курс валют", "Не удалось получить курс валюты"
    assert "доллара" in result, "В ответе нет 'доллара'"
    assert "руб" in result, "В ответе нет рублей"
    assert "коп" in result, "В ответе нет копеек"


def test_what_weather():
    """Тест функции погоды"""
    result = what_weather()
    error_messages = ["Ошибка на сервере погоды", "Сетевая ошибка", "Таймаут при запросе погоды"]
    assert not any(error in result for error in error_messages), f"Ошибка сервиса: {result}"


def test_prank():
    """Тест функции анекдотов"""
    from Oleg.utils.anecdote import an
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
    (min, 1, "минута"),
    (min, 2, "минуты"),
    (min, 5, "минут"),
    (min, 11, "минут"),
    (min, 21, "минута"),
    (min, 24, "минуты"),
])
def test_formatters_param(func, value, expected):
    """Параметризованный тест для всех склонений"""
    assert func(value) == expected, f"{func.__name__}({value}) должно быть '{expected}'"