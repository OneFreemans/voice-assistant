def parse_command(text: str, commands: dict):
    """
    Парсит текстовую команду.

    Args:
        text: Текст команды
        commands: Словарь команд (COMMANDS из main.py)

    Returns:
        (триггер, аргументы без триггера, словарь аргументов без триггера) или (None, None, None) если нет команды
    """
    for trigger in sorted(commands.keys(), key=len, reverse=True):
        if text.startswith(trigger + " ") or text == trigger:
            args_part = text[len(trigger):].strip()
            args = args_part.split()
            return trigger, args_part, args
    return None, None, None