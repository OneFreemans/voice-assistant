import tkinter as tk
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import main

class VoiceGUI:
    def __init__(self, master):
        self.root = master
        self.root.title("Oleg Assistant")
        self.root.geometry("300x200")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(False, False)

        self.voice_active = False
        self.voice_thread = None

        # Регистрируем лампы
        main.set_status_callback(self.on_status)

        # Индикатор (чёрный по умолчанию)
        self.indicator = tk.Canvas(root, width=30, height=30, bg='#1a1a2e', highlightthickness=0)
        self.indicator.create_oval(5, 5, 25, 25, fill='#2a2a3a', outline='')
        self.indicator.pack(pady=20)

        # Кнопки
        btn_frame = tk.Frame(root, bg='#1a1a2e')
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(
            btn_frame,
            text="Старт",
            font=('Arial', 12),
            bg='#2a2a3a',
            fg='#aaffaa',
            relief=tk.FLAT,
            padx=20,
            pady=5,
            command=self.start_voice
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(
            btn_frame,
            text="Стоп",
            font=('Arial', 12),
            bg='#2a2a3a',
            fg='#ffaaaa',
            relief=tk.FLAT,
            padx=20,
            pady=5,
            command=self.stop_voice,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)

    def on_status(self, status):
        """Вызывается из main.py при смене состояния"""
        if status == 1:
            # Активирован, жду команду
            self.indicator.itemconfig(1, fill='#33ff33')
        elif status == 0:
            # Вернулся в режим ожидания
            self.indicator.itemconfig(1, fill='#2a2a3a')

    def start_voice(self):
        if not self.voice_active:
            self.voice_active = True
            self.voice_thread = threading.Thread(target=self.voice_loop, daemon=True)
            self.voice_thread.start()
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.indicator.itemconfig(1, fill='#2a2a3a')  # чёрный

    def stop_voice(self):
        self.voice_active = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.indicator.itemconfig(1, fill='#2a2a3a')  # чёрный

    def voice_loop(self):
        try:
            while self.voice_active:
                main.listen_for_command()
        except Exception as e:
            print(f"Voice error: {e}")
            self.root.after(0, self.stop_voice)


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceGUI(root)
    root.mainloop()