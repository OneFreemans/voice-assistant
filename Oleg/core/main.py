from dataclasses import dataclass, field
from typing import Callable, List

from Oleg.commands.functions import (
    my_timer,
    time_kem,
    run_program,
    prank,
    what_weather,
    currency,
    what_dey,
    calculation_materials,
    open_website,
    search_yandex,
    print_heart,
    run_timer,
)
from Oleg.services.vk_functions import last_message, answer_last_message, messenger
from Oleg.core.voice import say_text, process_result_and_restart
from Oleg import config
import sys
import threading
import speech_recognition as sr
from time import sleep
from Oleg.utils.logger import logger
from Oleg.commands.smart_home import control_device
from Oleg.commands.notes import add_note, list_notes, delete_note, clear_notes
from Oleg.utils.command_parser import parse_command
from Oleg.commands.ai_chat import ai_chat_mode


# ------------------------------------------------------------------ CommandSpec ---


@dataclass(frozen=True)
class CommandSpec:
    """
    Описание одной голосовой команды.

    Аргументы:
        func:        Функция-обработчик.
        mode:        Режим передачи аргументов.
        nargs:       Кол-во позиционных аргументов (актуально для mode="pos").
        background:  Фоновая функция (таймер и т.п.), запускается в отдельном потоке.
        aliases:     Синонимы-фразы, которые ведут на этот же trigger.
    """

    func: Callable
    mode: str = "pos"  # "none" | "pos" | "rest" | "full"
    nargs: int = 0
    background: Callable = None
    aliases: List[str] = field(default_factory=list)


# ------------------------------------------------------------------- COMMANDS ---


COMMANDS = {
    "таймер": CommandSpec(my_timer, mode="pos", nargs=2, background=run_timer),
    "сколько время": CommandSpec(time_kem, mode="none"),
    "запусти": CommandSpec(run_program, mode="pos", nargs=1),
    "расскажи анекдот": CommandSpec(prank, mode="none"),
    "погода": CommandSpec(what_weather, mode="none"),
    "курс": CommandSpec(currency, mode="pos", nargs=1),
    "какой сегодня день": CommandSpec(what_dey, mode="none"),
    "рассчитай": CommandSpec(calculation_materials, mode="pos", nargs=1),
    "открой": CommandSpec(open_website, mode="pos", nargs=1),
    "яндекс": CommandSpec(search_yandex, mode="rest"),
    "отправь сообщение": CommandSpec(messenger, mode="rest"),
    "последнее сообщение": CommandSpec(last_message, mode="none"),
    "ответь на сообщение": CommandSpec(answer_last_message, mode="rest"),
    "сердце": CommandSpec(print_heart, mode="pos", nargs=2),
    "включи": CommandSpec(control_device, mode="full"),
    "выключи": CommandSpec(control_device, mode="full"),
    "добавь заметку": CommandSpec(add_note, mode="rest"),
    "заметки": CommandSpec(list_notes, mode="none"),
    "удали заметку": CommandSpec(delete_note, mode="pos", nargs=1),
    "удали все заметки": CommandSpec(clear_notes, mode="none"),
    "режим собеседника": CommandSpec(ai_chat_mode, mode="none"),
}


# -----------------------------------------tk-------------------------------------
_status_callback = None


def set_status_callback(callback: Callable[[int], None]) -> None:
    """
    Устанавливает функцию обратного вызова для изменения статуса голосового режима.

    Args:
        callback: Функция, принимающая один аргумент (int: 0 или 1) и возвращающая None.
    """
    global _status_callback
    _status_callback = callback


# -------------------начинаем прослушивание, определение команды-----------------
def listen_for_command() -> None:
    """
    Основная функция прослушивания команд.

    Слушает микрофон, распознаёт речь и проверяет команду активации "Олег".
    При успешной активации вызывает listen_for_command_after_activation().
    """
    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)

        try:
            logger.info("Ожидаю команду 'Олег'...")
            audio = r.listen(source, timeout=2, phrase_time_limit=3)
            text = r.recognize_google(audio, language="ru-RU")
            logger.debug(f"Распознано: {text}")

            if config.match_activation_command(text, ["Олег стоп"]):
                say_text("Пока.")
                sys.exit(0)

            elif config.match_activation_command(text, config.OLEG_COMMANDS):
                if _status_callback is not None:
                    _status_callback(1)  # noqa
                return listen_for_command_after_activation()
            else:
                return None

        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            return None
        except Exception as e:
            logger.error(f"Ошибка распознавания: {e}.")
            return None


def dispatch_command(text: str, commands: dict):
    """
    Универсальный диспетчер команд.

    Парсит текст, находит команду, передаёт аргументы в нужном режиме
    и запускает фоновую задачу (таймер и т.п.).

    Args:
        text: Распознанный голосом текст (уже без активатора "Олег").
        commands: Словарь COMMANDS из этого модуля.

    Returns:
        Строка-результат выполнения или сообщение об ошибке.
    """
    trigger, args_part, args = parse_command(text, commands)

    if not trigger:
        return None, None, None

    spec = commands[trigger]

    # ---------- проверка аргументов ----------
    if spec.mode == "pos" and len(args) < spec.nargs:
        return (
            f"Команда '{trigger}' требует минимум {spec.nargs} аргументов.",
            None,
            None,
        )

    # ---------- вызов ----------
    if spec.mode == "none":
        result = spec.func()

    elif spec.mode == "pos":
        result = spec.func(*args[: spec.nargs])

    elif spec.mode == "rest":
        result = spec.func(args_part)

    elif spec.mode == "full":
        result = spec.func(trigger, args_part)

    else:
        result = spec.func()

    # ---------- фоновая задача (таймер и т.п.) ----------
    if spec.background and result:
        # Костыль: таймер запускаем только по текстовому маркеру
        if "таймер запущен" in str(result):
            t = threading.Thread(
                target=spec.background,
                args=(args[0] if args else "1", args[1] if len(args) > 1 else "минут"),
                daemon=True,
            )
            t.start()

    return result, trigger, args


def listen_for_command_after_activation() -> None:
    """
    Прослушивает команды после активации "Олег".

    Обрабатывает команды через dispatch_command.
    """
    with sr.Microphone() as source:
        r = sr.Recognizer()
        try:
            logger.info("Ожидаю команду...")

            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language="ru-RU").lower()
            logger.debug(f"Команда: {text}")

            if "стоп" in text:
                say_text("До скорых встреч.")
                sys.exit(0)

            result, trigger, args = dispatch_command(text, COMMANDS)

            if not trigger:
                say_text(f"Я не знаю команду - {text}.")
                return

            if isinstance(result, str) and "требует минимум" in result:
                say_text(result)
                return

            process_result_and_restart(result)

            if _status_callback is not None:
                _status_callback(2)  # noqa

        except Exception as e:
            logger.error(f"Ошибка: {e}.")


# ---------------ТОЛЬКО ДЛЯ PYTEST(запуск с test_oleg.py - pytest)------------------------
def process_command_text(text: str):
    """
    Обрабатывает текст команды и возвращает результат.

    Для тестов:
        - Команды с mode="none"   → возвращает "нет аргументов"
        - Команды с mode="full"   → возвращает (trigger, args_part)
        - Команды с mode="rest"   → возвращает args_part
        - Команды с mode="pos"    → возвращает кортеж/строку аргументов
    """
    if "стоп" in text:
        return "До скорых встреч!"

    trigger, args_part, args = parse_command(text, COMMANDS)

    if not trigger:
        return f"Я не знаю команду - {text}"

    spec = COMMANDS[trigger]

    # ---------- проверка аргументов ----------
    if spec.mode == "pos" and len(args) < spec.nargs:
        return f"Команда '{trigger}' требует минимум {spec.nargs} аргументов."

    # ---------- заглушки для тестов ----------
    if spec.mode == "none":
        return "нет аргументов"

    elif spec.mode == "full":
        return trigger, args_part

    elif spec.mode == "rest":
        return args_part

    elif spec.mode == "pos":
        if len(args) == 1:
            return args[0]
        elif len(args) >= 2:
            return args[0], args[1]

    return "неправильное кол-во аргументов"


def main():
    """Точка входа для консольного режима."""
    logger.info("Для активации скажите 'Олег'")
    logger.info("Начинаю прослушивание!")

    while True:
        listen_for_command()
        sleep(0.1)


if __name__ == "__main__":
    main()
