import sys
import tkinter as tk
from Oleg.core.main import main
from Oleg.gui.tk_gui import VoiceGUI

if __name__ == "__main__":
    if "--gui" in sys.argv:
        root = tk.Tk()
        app = VoiceGUI(root)
        root.mainloop()
    else:
        main()
