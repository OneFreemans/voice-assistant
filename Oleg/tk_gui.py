import tkinter as tk
from tkinter import scrolledtext
import threading
from Oleg.main import set_status_callback, listen_for_command
from Oleg.utils.logger import logger, set_gui_callback


# -------------------------------------------------------------------
# Класс графического интерфейса голосового ассистента
# -------------------------------------------------------------------
class VoiceGUI:
    """
    Графический интерфейс для голосового ассистента на Tkinter.

    Отвечает за:
    - Запуск и остановку голосового режима
    - Отображение лога работы
    - Индикатор состояния (вкл/выкл)
    - Быстрые команды
    """
    def __init__(self, master: tk.Tk) -> None:
        """
        Инициализация интерфейса
        master: корневое окно tkinter
        """
        self.root = master
        self.root.title("Oleg Assistant")                     # заголовок окна
        self.root.geometry("650x500")                         # размеры: ширина x высота
        self.root.configure(bg='#1a1a2e')                     # тёмный фон
        self.root.resizable(False, False)                     # запрет изменения размера

        # Переменные состояния
        self.voice_active = False        # активен ли голосовой режим
        self.voice_thread = None         # поток для голосового режима
        self.log_area = None             # текстовое поле для логов

        # Регистрируем обратный вызов для логгера — теперь все logger.info() и т.д.
        # будут дублироваться в это окно через метод on_log
        set_gui_callback(self.on_log)

        # Регистрируем обратный вызов для статуса из main.py
        # main будет вызывать on_status(1) или on_status(0)
        set_status_callback(self.on_status)

        # --- Верхняя часть с индикатором ---
        top_frame = tk.Frame(self.root, bg='#1a1a2e')
        top_frame.pack(pady=10)

        # Индикатор — кружок, меняющий цвет (зелёный/чёрный)
        self.indicator = tk.Canvas(top_frame, width=30, height=30, bg='#1a1a2e', highlightthickness=0)
        self.indicator.create_oval(5, 5, 25, 25, fill='#2a2a3a', outline='')
        self.indicator.pack(pady=5)

        # --- Кнопки управления ---
        btn_frame = tk.Frame(self.root, bg='#1a1a2e')
        btn_frame.pack(pady=10)

        # Кнопка "Старт" — включает голосовой режим
        self.start_btn = tk.Button(
            btn_frame,
            text="Старт",
            font=('Arial', 12),
            bg='#2a2a3a',           # тёмный фон
            fg='#aaffaa',           # светло-зелёный текст
            relief=tk.FLAT,         # плоская кнопка
            padx=20,
            pady=5,
            command=self.start_voice
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        # Кнопка "Стоп" — выключает голосовой режим
        self.stop_btn = tk.Button(
            btn_frame,
            text="Стоп",
            font=('Arial', 12),
            bg='#2a2a3a',
            fg='#ffaaaa',           # светло-красный текст
            relief=tk.FLAT,
            padx=20,
            pady=5,
            command=self.stop_voice,
            state=tk.DISABLED       # изначально неактивна
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        # --- Лог-поле для вывода сообщений ---
        log_frame = tk.Frame(self.root, bg='#1a1a2e')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ScrolledText — текстовое поле с полосой прокрутки
        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            bg='#2a2a3a',           # тёмный фон
            fg='#c0c0d0',           # светлый текст
            font=('Consolas', 9),    # моноширинный шрифт
            wrap=tk.WORD,           # перенос по словам
            relief=tk.FLAT,
            insertbackground='white' # цвет курсора
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Автопрокрутка вниз (показывает последние сообщения)
        self.log_area.see(tk.END)

    # Обработчик сообщений из логгера
    def on_log(self, message: str) -> None:
        """
        Вызывается из логгера при каждом новом сообщении.

        Args:
            message: Текст сообщения для отображения в логе.
        """
        if self.log_area:
            # Безопасная передача из другого потока
            self.root.after(0, self._append_log, message)

    def _append_log(self, message: str) -> None:
        """
        Добавляет сообщение в лог-поле и прокручивает его вниз.

        Args:
            message: Текст сообщения для добавления.
        """
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)

    # Обработчик изменения статуса голосового режима
    def on_status(self, status: int) -> None:
        """
        Вызывается из main.py при смене состояния.

        Args:
            status: 1 — ассистент активирован (сказали "Олег"), ждёт команду;
                    0 — вернулся в режим ожидания.
        """
        if status == 1:
            self.indicator.itemconfig(1, fill='#33ff33')  # зелёный

        elif status == 2:
            self.indicator.itemconfig(1, fill='#2a2a3a')  # чёрный

    # Запуск голосового режима
    def start_voice(self) -> None:
        """
        Запускает голосовой режим в отдельном потоке.
        Обновляет состояние кнопок и индикатора.
        """
        if not self.voice_active:
            self.voice_active = True
            self.voice_thread = threading.Thread(target=self.voice_loop, daemon=True)
            self.voice_thread.start()

            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.indicator.itemconfig(1, fill='#2a2a3a')
            self.on_log("🎤 Голосовой режим активирован")

    # Остановка голосового режима
    def stop_voice(self) -> None:
        """
        Останавливает голосовой режим.
        Обновляет состояние кнопок и индикатора.
        """
        self.voice_active = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.indicator.itemconfig(1, fill='#2a2a3a')
        self.on_log("🔇 Голосовой режим остановлен")

    # Основной цикл голосового режима (работает в отдельном потоке)
    def voice_loop(self) -> None:
        """
        Основной цикл голосового режима, работает в отдельном потоке.
        Вызывает main.listen_for_command() для обработки команд.
        При ошибке останавливает голосовой режим через главный поток.
        """
        try:
            while self.voice_active:
                listen_for_command()
        except Exception as e:
            logger.error(f"Voice error: {e}")
            self.on_log(f"❌ Ошибка: {e}")
            self.root.after(0, self.stop_voice)   # noqa


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceGUI(root)
    root.mainloop()