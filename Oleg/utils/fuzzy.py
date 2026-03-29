"""Утилиты для fuzzy matching (нечёткое сопоставление строк)"""

from difflib import SequenceMatcher

# Порог схожести для fuzzy matching (0-100)
FUZZY_THRESHOLD = 78


def match_activation_command(text: str, commands: list, threshold: int = None) -> bool:
    """
    Проверяет, соответствует ли текст одной из команд активации.
    Использует нечёткое сопоставление (fuzzy matching).
    
    Args:
        text: распознанный текст
        commands: список команд для сравнения
        threshold: порог схожести (0-100), по умолчанию FUZZY_THRESHOLD
    
    Returns:
        True если команда найдена с достаточной схожестью
    """
    if threshold is None:
        threshold = FUZZY_THRESHOLD
    
    text_lower = text.lower().strip()
    
    # Точное совпадение (без fuzzy)
    if text_lower in [cmd.lower() for cmd in commands]:
        return True
    
    # Нечёткое сопоставление
    for cmd in commands:
        similarity = SequenceMatcher(None, text_lower, cmd.lower()).ratio() * 100
        if similarity >= threshold:
            return True
    
    return False
