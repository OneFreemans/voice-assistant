def parse_command(text: str, commands: dict):
    """
    Парсит текстовую команду.

    Поддерживает синонимы: если команда имеет aliases,
    они добавляются к списку триггеров и проверяются на совпадение.

    При совпадении синонима возвращает реальный ключ команды.

    Args:
        text: Текст команды
        commands: Словарь команд (COMMANDS из main.py)

    Returns:
        (реальный_триггер, аргументы без триггера, список аргументов) или
        (None, None, None) если нет команды
    """
    # Собираем все триггеры + синонимы
    all_triggers = []
    for trigger, spec in commands.items():
        all_triggers.append(trigger)
        all_triggers.extend(spec.aliases)

    # Сортируем по убыванию длины — "удали все заметки" матчится до "удали заметку"
    for trigger in sorted(all_triggers, key=len, reverse=True):
        if text.startswith(trigger + " ") or text == trigger:
            args_part = text[len(trigger) :].strip()
            args = args_part.split()

            # Если триггер — синоним, вернём реальный ключ
            real_key = trigger
            if trigger not in commands:
                for real, spec in commands.items():
                    if trigger in spec.aliases:
                        real_key = real
                        break

            return real_key, args_part, args

    return None, None, None
