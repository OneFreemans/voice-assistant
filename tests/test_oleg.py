from Oleg.commands.functions import (
    time_kem,
    what_dey,
    what_weather,
    currency,
    prank,
    my_timer,
    print_heart,
    search_yandex,
    run_program,
    open_website,
)
from Oleg.commands.notes import (
    _load_notes,
    _save_notes,
    add_note,
    delete_note,
    list_notes,
    clear_notes,
)
import pytest
from unittest.mock import patch, MagicMock, mock_open
from Oleg.core.main import process_command_text
from Oleg.services.vk_functions import last_message
from Oleg.commands.smart_home import control_device
from Oleg.utils.formatters import mesh, rub, cop, min as format_min
from Oleg.commands.functions import _process_calculation, calculation_materials
from Oleg.commands.ai_chat import ask_ai
from Oleg.utils.anecdote import an
from Oleg import config
import json

# pytest --cov=Oleg --cov-report=html


class TestBasicFunctions:
    """Базовые функции: время, дата, курс, погода, анекдоты"""

    def test_time_kem(self):
        """Тест функции времени"""
        result = time_kem()
        assert len(result) == 8, f"Неправильная длина строки: {len(result)} вместо 8"

    def test_what_dey(self):
        """Тест функции даты"""
        result = what_dey()
        assert len(result) == 18, (
            f"what_dey() -> Неправильная длина строки: {len(result)} вместо 18"
        )

    def test_currency(self):
        """Тест функции курса валют"""
        # Тест для доллара
        result_usd = currency("доллар")
        assert result_usd != "Не удалось получить курс с сайта ЦБ", (
            "Не удалось получить курс доллара"
        )
        assert "курс доллара" in result_usd, "В ответе нет 'курс доллара'"
        assert "руб" in result_usd or "рублей" in result_usd, "В ответе нет рублей"

        # Тест для евро
        result_eur = currency("евро")
        assert result_eur != "Не удалось получить курс с сайта ЦБ", (
            "Не удалось получить курс евро"
        )
        assert "курс евро" in result_eur, "В ответе нет 'курс евро'"
        assert "руб" in result_eur or "рублей" in result_eur, "В ответе нет рублей"

        # Тест для неизвестной валюты
        result_unknown = currency("фунт")
        assert result_unknown == "Не удалось обработать запрос на курс валют", (
            "Должна быть ошибка для неизвестной валюты"
        )

    def test_what_weather(self):
        result = what_weather()
        assert isinstance(result, str)
        assert len(result) > 0
        assert "ошибка" not in result.lower()

    def test_prank(self):
        """Тест функции анекдотов"""
        result = prank()
        assert result in an, "Анекдот не из списка"
        assert len(result) > 0, "Анекдот пустой"


class TestFormatters:
    """Тесты форматтеров (склонение слов)"""

    @pytest.mark.parametrize(
        "func, value, expected",
        [
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
        ],
    )
    def test_formatters_param(self, func, value, expected):
        """Параметризованный тест для всех склонений"""
        assert func(value) == expected, (
            f"{func.__name__}({value}) должно быть '{expected}'"
        )


class TestTimerAndHeart:
    """Таймер и сердечки"""

    def test_my_timer(self):
        """Тест функции таймера"""
        result_min = my_timer("5", "минут")
        assert "5" in result_min
        assert "минут" in result_min

        result_hour = my_timer("2", "часа")
        assert "2" in result_hour
        assert "часа" in result_hour

        result_unknown = my_timer("3", "секунды")
        assert "Неизвестный формат" in result_unknown

    def test_print_heart(self):
        """Тест функции рисования сердечек (только возврат. Печать не проверяется)"""
        result = print_heart("3", "красное")
        assert "Нарисовано 3 сердец" in result
        assert "красное" in result


class TestWebAndPrograms:
    """Работа с сайтами и программами"""

    def test_open_website(self):
        """Тест открытия сайта — мокаем webbrowser, чтобы не открывать браузер"""
        with patch("Oleg.commands.functions.webbrowser") as mock_webbrowser:
            result_ok = open_website("вк")
            assert "открыт" in result_ok
            mock_webbrowser.open_new_tab.assert_called_once_with("https://vk.com")

            mock_webbrowser.reset_mock()

            result_bad = open_website("несуществующийсайт")
            assert "не найден" in result_bad
            mock_webbrowser.open_new_tab.assert_not_called()

    def test_search_yandex(self):
        """Тест поиска в Яндексе — мокаем webbrowser"""
        with patch("Oleg.commands.functions.webbrowser") as mock_webbrowser:
            result_ok = search_yandex("яндекс погода")
            assert "Открываю ссылку" in result_ok
            mock_webbrowser.open_new_tab.assert_called_once()

            mock_webbrowser.reset_mock()

            result_bad = search_yandex("яндекс")
            assert "Запрос не указан" in result_bad
            mock_webbrowser.open_new_tab.assert_not_called()

    def test_run_program_all_scenarios(self):
        """Все сценарии run_program в одном тесте"""

        with patch("Oleg.commands.functions.subprocess.Popen") as mock_popen:
            # 1. Успешный запуск
            mock_process = MagicMock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process
            result = run_program("steam")
            assert "запускается" in result
            mock_popen.reset_mock()

            # 2. Файл не найден
            mock_popen.side_effect = FileNotFoundError
            result = run_program("steam")
            assert "не найден" in result
            mock_popen.reset_mock()

            # 3. Нет прав
            mock_popen.side_effect = PermissionError
            result = run_program("steam")
            assert "Нет прав" in result
            mock_popen.reset_mock()

            # 4. Общая ошибка
            mock_popen.side_effect = Exception("Ошибка")
            result = run_program("steam")
            assert "Ошибка при запуске" in result


class TestSmartHome:
    """Управление умным домом"""

    def test_control_device(self):
        """Тест управления устройством с моком"""
        with patch("Oleg.commands.smart_home.control_yandex_device") as mock_yandex:
            mock_yandex.return_value = "Устройство включено"
            with patch.dict(config.YANDEX_DEVICE_IDS, {"свет": "test_id"}):
                result = control_device("включи", "свет")
                assert "Устройство" in result
                mock_yandex.assert_called_once_with("test_id", "on")


class TestVK:
    """Работа с VK API"""

    def test_last_message(self):
        """Тест last_message с моком"""
        mock_vk = MagicMock()
        mock_vk.messages.getConversations.return_value = {
            "count": 1,
            "items": [{"last_message": {"from_id": 123, "text": "Тестовое сообщение"}}],
        }
        mock_vk.users.get.return_value = [{"first_name": "Тест", "last_name": "Тестов"}]

        with patch("Oleg.services.vk_functions.vk", mock_vk):
            result = last_message()
            assert "Тест Тестов" in result
            assert "Тестовое сообщение" in result


class TestProcessCommand:
    """Маршрутизация команд"""

    @pytest.mark.parametrize(
        "command, expected",
        [
            # КОМАНДЫ С return trigger, args_part (min_args = -2)
            ("включи свет в комнате", ("включи", "свет в комнате")),
            ("выключи свет", ("выключи", "свет")),
            # КОМАНДЫ С return args_part (min_args = -1)
            ("отправь сообщение Тест Тестов привет", "Тест Тестов привет"),
            ("ответь на сообщение спасибо", "спасибо"),
            # КОМАНДЫ С return args[0] (min_args = 1)
            ("открой вк", "вк"),
            ("запусти steam", "steam"),
            ("курс доллар", "доллар"),
            ("курс евро", "евро"),
            ("удали заметку 5", "5"),
            # КОМАНДЫ С return (args[0], args[1]) (min_args = 2)
            ("таймер 5 минут", ("5", "минут")),
            ("сердце 5 красное", ("5", "красное")),
            # КОМАНДЫ С return "нет аргументов" (min_args = 0)
            ("последнее сообщение", "нет аргументов"),
            ("сколько время", "нет аргументов"),
            ("расскажи анекдот", "нет аргументов"),
            ("погода", "нет аргументов"),
            ("какой сегодня день", "нет аргументов"),
            ("заметки", "нет аргументов"),
            ("удали все заметки", "нет аргументов"),
            ("стоп", "До скорых встреч!"),
        ],
    )
    def test_process_command_text(self, command, expected):
        """Параметризованный тест для проверки маршрутизации команд"""
        assert process_command_text(command) == expected

    @pytest.mark.parametrize(
        "command, expected_substring",
        [
            ("что-то непонятное", "Я не знаю команду"),
            ("таймер", "требует минимум 2 аргументов"),
            ("сердце 5", "требует минимум 2 аргументов"),
        ],
    )
    def test_process_command_text_errors(self, command, expected_substring):
        """Параметризованный тест для проверки ошибок маршрутизации команд"""
        assert expected_substring in process_command_text(command)


@pytest.fixture
def temp_notes_file(tmp_path):
    """Временный файл для заметок (не мешает реальному)"""
    notes_file = tmp_path / "notes.json"
    with patch("Oleg.commands.notes.NOTES_FILE", str(notes_file)):
        yield notes_file


class TestNotes:
    """Все тесты для заметок (загрузка/сохранение + операции)"""

    # ===== ЗАГРУЗКА / СОХРАНЕНИЕ =====

    def test_load_notes_file_not_found(self, temp_notes_file):
        """Файла нет → пустой список"""
        assert _load_notes() == []

    def test_load_notes_invalid_json(self, temp_notes_file):
        """Битый JSON → пустой список"""
        temp_notes_file.write_text("{invalid json", encoding="utf-8")
        assert _load_notes() == []

    def test_load_notes_no_notes_key(self, temp_notes_file):
        """JSON без ключа 'notes' → пустой список"""
        temp_notes_file.write_text('{"other": []}', encoding="utf-8")
        assert _load_notes() == []

    def test_load_notes_ok(self, temp_notes_file):
        """Нормальный JSON → список заметок"""
        temp_notes_file.write_text(
            '{"notes": ["купить хлеб", "позвонить маме"]}', encoding="utf-8"
        )
        notes = _load_notes()
        assert notes == ["купить хлеб", "позвонить маме"]

    def test_save_notes_ok(self, temp_notes_file):
        """Сохранение работает → файл создаётся, данные корректны"""
        notes = ["заметка 1", "заметка 2"]
        _save_notes(notes)
        with open(temp_notes_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data == {"notes": notes}

    @patch("Oleg.commands.notes.logger")
    def test_save_notes_ioerror(self, mock_logger, temp_notes_file):
        """Ошибка записи → не падает, логирует"""
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = IOError("Disk full")
            _save_notes(["заметка"])
            mock_logger.error.assert_called_once()

    # ===== ОПЕРАЦИИ С ЗАМЕТКАМИ =====

    def test_add_note_empty(self):
        """Пустая заметка → отказ"""
        result = add_note("")
        assert result == "Нельзя добавить пустую заметку"

    def test_add_note_whitespace(self):
        """Пробелы → отказ"""
        result = add_note("   ")
        assert result == "Нельзя добавить пустую заметку"

    def test_add_note_ok(self, temp_notes_file):
        """Нормальная заметка → добавляется"""
        result = add_note("купить молоко")
        assert result == "Заметка добавлена: купить молоко"
        assert _load_notes() == ["купить молоко"]

    def test_delete_note_no_notes(self, temp_notes_file):
        """Нет заметок → сообщение"""
        result = delete_note("1")
        assert result == "Нет заметок для удаления"

    def test_delete_note_invalid_number(self, temp_notes_file):
        """Некорректный номер → отказ"""
        add_note("заметка")
        result = delete_note("abc")
        assert "Некорректный номер" in result

    def test_delete_note_out_of_range(self, temp_notes_file):
        """Номер больше длины списка → отказ"""
        add_note("заметка")
        result = delete_note("10")
        assert "Нет заметки с номером 10 (всего 1)" in result

    def test_delete_note_by_digit(self, temp_notes_file):
        """Удаление по цифре → удаляется"""
        add_note("заметка 1")
        add_note("заметка 2")
        result = delete_note("2")
        assert result == "Удалена заметка 2: заметка 2"
        assert _load_notes() == ["заметка 1"]

    @pytest.mark.parametrize(
        "word, expected_index", [("один", 1), ("два", 2), ("три", 3)]
    )
    def test_delete_note_by_word(self, temp_notes_file, word, expected_index):
        """Удаление по слову → удаляется"""
        add_note("заметка 1")
        add_note("заметка 2")
        add_note("заметка 3")
        result = delete_note(word)
        assert f"Удалена заметка {expected_index}" in result
        assert f"заметка {expected_index}" not in _load_notes()

    def test_delete_note_negative(self, temp_notes_file):
        """Отрицательный номер → отказ"""
        add_note("заметка")
        result = delete_note("-5")
        assert "Нет заметки" in result

    def test_list_notes_empty(self, temp_notes_file):
        """Нет заметок → сообщение"""
        assert list_notes() == "Заметок пока нет"

    def test_list_notes_ok(self, temp_notes_file):
        """Есть заметки → форматированный список"""
        add_note("купить хлеб")
        add_note("позвонить маме")
        result = list_notes()
        assert "Ваши заметки:" in result
        assert "1. купить хлеб" in result
        assert "2. позвонить маме" in result

    def test_list_notes_long_line(self, temp_notes_file):
        """Длинная заметка обрезается до 50 символов"""
        long_text = "а" * 100
        add_note(long_text)
        result = list_notes()
        assert "..." in result
        assert len(result.split("\n")[1]) <= 55

    def test_clear_notes_confirm(self, monkeypatch, temp_notes_file):
        """Подтверждение 'y' → все заметки удалены"""
        add_note("заметка")
        monkeypatch.setattr("builtins.input", lambda _: "y")
        result = clear_notes()
        assert result == "Все заметки удалены"
        assert _load_notes() == []

    def test_clear_notes_cancel(self, monkeypatch, temp_notes_file):
        """Отмена 'n' → заметки остаются"""
        add_note("заметка")
        monkeypatch.setattr("builtins.input", lambda _: "n")
        result = clear_notes()
        assert result == "Удаление отменено"
        assert _load_notes() == ["заметка"]

    def test_clear_notes_empty_input(self, monkeypatch, temp_notes_file):
        """Пустой ввод → удаление отменено (первый символ не 'y')"""
        add_note("заметка")
        monkeypatch.setattr("builtins.input", lambda _: "")
        result = clear_notes()
        assert result == "Удаление отменено"
        assert _load_notes() == ["заметка"]


class TestCalculationMaterials:
    """Тесты для расчёта материалов (стяжка, наливной пол)"""

    # ========== ЧИСТАЯ ЛОГИКА (_process_calculation) ==========

    def test_process_calculation_stiazka_ok(self):
        """Стяжка, правильные данные"""
        result = _process_calculation("стяжку", "40 квадратов 5 сантиметров")
        assert "Понадобится" in result
        assert "мешка" in result
        assert "материал уйдёт" in result
        assert "работу возьмите" in result

    def test_process_calculation_nalivnoy_ok(self):
        """Наливной пол, правильные данные"""
        result = _process_calculation("наливной", "20 квадратов 3 сантиметра")
        assert "Понадобится" in result
        assert "материал уйдёт" in result

    def test_process_calculation_invalid_mat(self):
        """Неизвестный материал -> ошибка парсинга (так как текст без слов)"""
        result = _process_calculation("неизвестно", "40 5")
        assert "Не удалось распознать данные" in result

    def test_process_calculation_too_few_words(self):
        """Слишком мало слов в тексте"""
        result = _process_calculation("стяжку", "40 5")
        assert "Не удалось распознать данные" in result

    def test_process_calculation_invalid_numbers(self):
        """Не числа вместо данных -> ошибка парсинга (нет слов 'квадратов')"""
        result = _process_calculation("стяжку", "сорок пять")
        assert "Не удалось распознать данные" in result

    def test_process_calculation_negative_area(self):
        """Отрицательная площадь -> ошибка парсинга (нет слов 'квадратов')"""
        result = _process_calculation("стяжку", "-5 10 сантиметров")
        assert "Не удалось распознать числа" in result

    def test_process_calculation_zero_thickness(self):
        """Нулевая толщина -> ошибка парсинга (нет слов 'квадратов')"""
        result = _process_calculation("стяжку", "10 0")
        assert "Не удалось распознать данные" in result

    # ========== ИНТЕГРАЦИЯ С ГОЛОСОМ (calculation_materials) ==========

    def test_calculation_materials_voice_ok(self):
        with patch("Oleg.commands.functions.get_text_from_microphone") as mock_voice:
            mock_voice.return_value = "40 квадратов 5 сантиметров"
            result = calculation_materials("стяжку")
            assert "Понадобится" in result

    def test_calculation_materials_voice_none(self):
        """Микрофон не распознал речь"""
        with patch("Oleg.commands.functions.get_text_from_microphone") as mock_voice:
            mock_voice.return_value = None
            result = calculation_materials("стяжку")
            assert "Не удалось распознать речь" in result

    def test_calculation_materials_voice_invalid_text(self):
        """Микрофон вернул мусор"""
        with patch("Oleg.commands.functions.get_text_from_microphone") as mock_voice:
            mock_voice.return_value = "мусор"
            result = calculation_materials("стяжку")
            assert "Не удалось распознать данные" in result


class TestAiChat:
    """Тесты для функций AI-собеседника (без реальных API-вызовов)."""

    # ========== ТЕСТЫ ask_ai ==========

    @patch("Oleg.commands.ai_chat.requests.post")
    def test_ask_ai_success(self, mock_post):
        """Успешный запрос к API: возвращается ответ и обновляется история."""
        # Подменяем ответ API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Привет, брат!"}}]
        }
        mock_post.return_value = mock_response

        answer, history = ask_ai("как дела?", [])

        assert answer == "Привет, брат!"
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "как дела?"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Привет, брат!"

        # Проверяем, что запрос ушёл с правильными параметрами
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "deepseek-chat"

    @patch("Oleg.commands.ai_chat.requests.post")
    def test_ask_ai_with_history(self, mock_post):
        """Запрос с историей: история правильно расширяется."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Норм, сам как?"}}]
        }
        mock_post.return_value = mock_response

        existing_history = [
            {"role": "user", "content": "Привет"},
            {"role": "assistant", "content": "Здорово!"},
        ]

        answer, new_history = ask_ai("как дела?", existing_history)

        assert answer == "Норм, сам как?"
        assert len(new_history) == 4
        assert new_history[0]["role"] == "user"
        assert new_history[0]["content"] == "Привет"
        assert new_history[2]["role"] == "user"
        assert new_history[2]["content"] == "как дела?"

    @patch("Oleg.commands.ai_chat.requests.post")
    def test_ask_ai_network_error(self, mock_post):
        """Ошибка сети: возвращается сообщение об ошибке, история не меняется."""
        mock_post.side_effect = Exception("Connection timeout")

        original_history = [
            {"role": "user", "content": "old"},
            {"role": "assistant", "content": "old"},
        ]
        answer, new_history = ask_ai("вопрос", original_history.copy())

        assert answer == "Извини, не могу ответить сейчас."
        assert new_history == original_history

    @patch("Oleg.commands.ai_chat.requests.post")
    def test_ask_ai_http_error(self, mock_post):
        """HTTP ошибка API: возвращается сообщение об ошибке."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("HTTP 500")
        mock_post.return_value = mock_response

        answer, history = ask_ai("вопрос", [])

        assert answer == "Извини, не могу ответить сейчас."
        assert history == []

    @patch("Oleg.commands.ai_chat.requests.post")
    def test_ask_ai_history_truncation(self, mock_post):
        """История урезается до 10 сообщений (+ новые)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "ok"}}]}
        mock_post.return_value = mock_response

        # Создаём длинную историю (10 старых сообщений = 5 диалогов)
        long_history = []
        for i in range(10):
            long_history.append({"role": "user", "content": f"q{i}"})
            long_history.append({"role": "assistant", "content": f"a{i}"})

        # 10 сообщений уже есть, добавляем ещё один диалог
        _, new_history = ask_ai("последний вопрос", long_history)

        # Должно быть не больше 12: 10 старых + user + assistant
        assert len(new_history) <= 12
        # Последнее сообщение должно быть от ассистента
        assert new_history[-1]["role"] == "assistant"
        assert new_history[-2]["role"] == "user"
        assert new_history[-2]["content"] == "последний вопрос"

    # ========== ИНТЕГРАЦИЯ (проверка импорта) ==========

    def test_ai_chat_mode_import(self):
        """Проверка, что функция ai_chat_mode импортируется без ошибок."""
        try:
            from Oleg.commands.ai_chat import ai_chat_mode

            assert callable(ai_chat_mode)
        except ImportError as e:
            pytest.fail(f"Не удалось импортировать ai_chat_mode: {e}")
