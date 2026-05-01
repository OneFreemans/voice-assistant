import re
from typing import Union

WORD_TO_NUMBER = {
    "один": 1,
    "два": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
}


def extract_number(text: Union[str, int]):
    """
    Извлекает число из текста.
    Поддерживает цифры (1, 2, 3, ...) и словесную запись (один, два, ...).

    Args:
        text: Строка, в которой нужно найти число.

    Returns:
        Число или None, если число не найдено.

    Examples:
        >>> extract_number("удали заметку 5")
        5
        >>> extract_number("удали заметку шесть")
        6
        >>> extract_number("нет числа")
        None
    """
    match = re.search(r"\d+", text)
    if match:
        return int(match.group())

    if text.lower() in WORD_TO_NUMBER:
        return WORD_TO_NUMBER[text.lower()]

    return None
