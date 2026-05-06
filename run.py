import sys
import tkinter as tk
from Oleg.core.main import main
from Oleg.gui.tk_gui import VoiceGUI
from Oleg.core.voice import _get_silero_model
import pygame

if __name__ == "__main__":
    pygame.mixer.init()
    _get_silero_model()

    if "--gui" in sys.argv:
        root = tk.Tk()
        app = VoiceGUI(root)
        root.mainloop()
    else:
        main()
