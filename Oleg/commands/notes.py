"""
Модуль для работы с заметками (блокнот).

Хранит заметки в JSON-файле, предоставляет функции для добавления,
удаления, просмотра и очистки через голосовые команды.
"""

import json
import os
from typing import List, Union
from Oleg.utils.logger import logger
from Oleg.utils.number_utils import extract_number

NOTES_FILE = os.path.join(os.path.dirname(__file__), "notes.json")

# ---------- Внутренние функции ----------


def _load_notes() -> List[str]:
    """
    Загрузить заметки из JSON-файла.

    Returns:
        List[str]: Список заметок. Если файл не найден или повреждён — пустой список.
    """
    if not os.path.exists(NOTES_FILE):
        return []

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("notes", [])
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Ошибка загрузки заметок: {e}.")
        return []


def _save_notes(notes: List[str]) -> None:
    """
    Сохранить заметки в JSON-файл.

    Args:
        notes: Список заметок.

    Returns:
        None
    """
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump({"notes": notes}, f, ensure_ascii=False, indent=4)
    except IOError as e:
        logger.error(f"Ошибка сохранения заметок: {e}.")


# ---------- Публичные функции ----------


def add_note(text: str) -> str:
    """
    Добавить новую заметку.

    Args:
        text: Текст заметки.

    Returns:
        Сообщение о результате операции.
    """
    if not text or not text.strip():
        return "Нельзя добавить пустую заметку."

    notes = _load_notes()
    notes.append(text.strip())
    _save_notes(notes)
    return f"Заметка добавлена: {text}."


def delete_note(number: Union[str, int]) -> str:
    """
    Удалить заметку по индексу (1-based).

    Args:
        number: Номер заметки (1, 2, 3... или "один", "два", "три"...).

    Returns:
        Сообщение о результате операции.
    """
    index = extract_number(number.strip())  # приводит "один" к 1, "два" к 2 и Т.Д..
    if index is None or index <= 0:
        return f"Некорректный номер: {number}."

    notes = _load_notes()

    if not notes:
        return "Нет заметок для удаления."

    try:
        idx = int(index) - 1
    except (ValueError, TypeError):
        return f"Некорректный номер: {index}."

    if idx < 0 or idx >= len(notes):
        return f"Нет заметки с номером {index} (всего {len(notes)})."

    removed = notes.pop(idx)
    _save_notes(notes)
    return f"Удалена заметка {index}: {removed}."


def list_notes() -> str:
    """
    Получить список всех заметок в текстовом виде.

    Returns:
        Текст с нумерованным списком заметок или сообщение, что заметок нет.
    """
    notes = _load_notes()

    if not notes:
        return "Заметок пока нет."

    result = "Ваши заметки:\n"
    for i, note in enumerate(notes, 1):
        max_len = 50
        short_note = note if len(note) <= max_len else note[: max_len - 3] + "..."
        result += f"{i}. {short_note}\n"

    return result


def clear_notes() -> str:
    """
    Удалить все заметки.

    Returns:
        Сообщение о результате операции.
    """
    ans = (
        input("Заметки будут удалены безвозвратно!\nВы уверены? [y/n]").lower().strip()
    )
    if ans.startswith("y"):
        _save_notes([])
        return "Все заметки удалены."
    else:
        return "Удаление отменено."


# def get_all_notes() -> List[str]: TODO прикрутить к gui
#     """
#     Получить сырой список заметок (для GUI).
#
#     Returns:
#         Список заметок.
#     """
#     return _load_notes()
