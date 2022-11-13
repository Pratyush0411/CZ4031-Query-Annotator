import interface
import tkinter as tk


# RUN PROJECT.PY TO START THE GUI
if __name__ == '__main__':
    root = tk.Tk()
    app = interface.UserInterface(root)

    root.mainloop()
