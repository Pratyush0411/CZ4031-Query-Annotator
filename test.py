import turtle
import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import *
from tkinter import ttk
import main


class UserInterface:

    font = ("Segoe", 12)

    def __init__(self, master):
        self.canvaswidth = 1200
        self.canvasheight = 400

        # MAIN WINDOW
        self.master = master
        self.master.title("CZ4031-QUERY-ANNOTATOR")
        self.master.geometry(str(self.canvaswidth) +
                             "x" + str(self.canvasheight))
        self.frame1 = Frame(self.master, width=self.canvaswidth /
                            2, height=self.canvasheight, bg="BLUE")
        self.frame1.pack(side=tk.LEFT)

        self.frame2 = Frame(self.master, width=self.canvaswidth/2,
                            height=self.canvasheight, bg="YELLOW")
        self.frame2.pack(side=tk.LEFT)

        self.text = tk.Label(self.frame2, text="Hello")
        self.text.pack()


if __name__ == '__main__':
    root = tk.Tk()
    app = UserInterface(root)

    root.mainloop()
