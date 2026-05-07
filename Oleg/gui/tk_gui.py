import customtkinter as ctk
import threading
from Oleg.core.main import set_status_callback, listen_for_command
from Oleg.utils.logger import logger, set_gui_callback


BACKGROUND = "#0D1117"
FRAME_BG = "#161B22"
BUTTON_BG = "#21262D"
BUTTON_HOVER = "#30363D"
GREEN_ACCENT = "#3FB950"
RED_ACCENT = "#F85149"
TEXT_COLOR = "#C9D1D9"
TEXT_MUTED = "#8B949E"


class VoiceGUI:
    def __init__(self, master: ctk.CTk) -> None:
        self.root = master
        self.root.title("Oleg Assistant")
        self.root.geometry("600x450")
        ctk.set_appearance_mode("Dark")
        self.root.resizable(False, False)

        self.voice_active = False
        self.voice_thread = None

        set_gui_callback(self.on_log)
        set_status_callback(self.on_status)

        self._build_ui()

    def _build_ui(self):
        # --- Основной контейнер ---
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Заголовок ---
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        title = ctk.CTkLabel(
            header_frame,
            text="🎙️ Oleg",
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT_COLOR,
        )
        title.pack(side="left")

        # --- Индикатор статуса ---
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="● Ожидание",
            font=("Segoe UI", 19),
            text_color=TEXT_MUTED,
        )
        self.status_label.pack(anchor="w", padx=(390, 0))

        # --- Кнопки управления ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))

        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ Старт",
            width=130,
            height=36,
            font=("Segoe UI", 12, "bold"),
            fg_color=GREEN_ACCENT,
            hover_color="#2EA043",
            text_color="#000000",
            text_color_disabled="#FFFFFF",
            corner_radius=8,
            command=self.start_voice,
        )
        self.start_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Стоп",
            width=130,
            height=36,
            font=("Segoe UI", 12, "bold"),
            fg_color=RED_ACCENT,
            hover_color="#D0352A",
            text_color="#000000",
            text_color_disabled="#FFFFFF",
            corner_radius=8,
            command=self.stop_voice,
            state="disabled",
        )
        self.stop_btn.pack(side="left")

        # --- Лог-поле ---
        self.log_area = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=("Cascadia Code", 10),
            fg_color=FRAME_BG,
            text_color=TEXT_COLOR,
            border_width=1,
            border_color="#30363D",
            corner_radius=10,
        )
        self.log_area.pack(fill="both", expand=True)

        self.log_area.tag_config("system", foreground=TEXT_MUTED)
        self.log_area.tag_config("success", foreground=GREEN_ACCENT)
        self.log_area.tag_config("error", foreground=RED_ACCENT)

    def on_log(self, level: int, message: str) -> None:
        if self.log_area and level >= 20:
            tag = "system"
            if "активирован" in message or "✅" in message:
                tag = "success"
            elif "Ошибка" in message or "❌" in message:
                tag = "error"
            self.root.after(0, self._append_log, message, tag)

    def _append_log(self, message: str, tag: str = "system") -> None:
        self.log_area.insert("end", f"{message}\n", tag)
        self.log_area.see("end")

    def on_status(self, status: int) -> None:
        if status == 1:
            self.status_label.configure(text="● Активен", text_color=GREEN_ACCENT)
        elif status == 2:
            self.status_label.configure(text="● Ожидание", text_color=TEXT_MUTED)

    def start_voice(self) -> None:
        if not self.voice_active:
            self.voice_active = True
            self.voice_thread = threading.Thread(target=self.voice_loop, daemon=True)
            self.voice_thread.start()

            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.on_log(20, "▶ Голосовой режим активирован")

    def stop_voice(self) -> None:
        self.voice_active = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="● Ожидание", text_color=TEXT_MUTED)
        self.on_log(20, "⏹ Голосовой режим остановлен")

    def voice_loop(self) -> None:
        try:
            while self.voice_active:
                listen_for_command()
        except Exception as e:
            logger.error(f"Voice error: {e}")
            self.on_log(40, f"❌ Ошибка: {e}")
            self.root.after(0, self.stop_voice)
