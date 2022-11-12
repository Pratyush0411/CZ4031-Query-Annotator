import turtle
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from annotationmultiq import Annotator


class UserInterface:
    def __init__(self, master):
        self.master = master
        self.master.title("CZ4031-QUERY-ANNOTATOR")
        self.canvas = tk.Canvas(master)
        self.canvas.config(width=1200, height=600)
        self.canvas.pack(side=tk.LEFT)

        self.textfield = tk.Text(root, height = 5, width = 50, font= ("Segoe",12))
        self.sendQueryButton = tk.Button(self.master, text = "Send Query", command = self.get_input)
        self.label = tk.Label(root, text = "Enter your Query to optimize")
        
        
        self.label.config(font = ("Segoe",12))
        self.label.pack()
        self.textfield.pack()
        self.sendQueryButton.pack()

        self.screen = turtle.TurtleScreen(self.canvas)
        self.screen.bgcolor("white")
        

        print(self.screen.window_height(), self.screen.window_width())
        # self.canvas.create_window(300, 300, window = self.button)
        
    
    def get_input(self):
        query = self.textfield.get("1.0","end-1c")
        # print(query)
        self.label1 = tk.Label(root, text = query)
        self.canvas.create_window(200,230, window = self.label1)

        query = "select * from customer C, orders O where C.c_custkey = O.o_custkey and A = B"
        annotationList = {"customer C": ["This is the first annotation"],
                        "C.c_custkey = O.o_custkey": ["This is the second annotation that is a bit longer than the other ones and spans more than one line"],
                        "A = B": ["This is the third annotation"], "orders O": ["This is the 4th one"]}

        self.instance = Annotator(query,annotationList)
        wordannoidx, wordList = Annotator.annotation_matcher(self.instance)
 
        Annotator.turtle_drawer(self, wordannoidx, wordList, annotationList)
    

if __name__ == '__main__':
    root = tk.Tk()
    app = UserInterface(root)

    root.mainloop()


###
# self.screen = turtle.TurtleScreen(self.canvas)
# self.screen.bgcolor("cyan")
# self.button = tk.Button(self.master, text="Press me", command=self.press)
# self.button.pack()
