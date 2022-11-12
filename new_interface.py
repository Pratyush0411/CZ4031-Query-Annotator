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
        

    def do_stuff(self):
        for color in ["red", "yellow", "green"]:
            self.my_lovely_turtle.color(color)
            self.my_lovely_turtle.right(120)
    
    def get_input(self):
        query = self.textfield.get("1.0","end-1c")
        print(query)
        self.label1 = tk.Label(root, text = query)
        self.canvas.create_window(200,230, window = self.label1)

        self.turtle_drawer()

    def turtle_drawer(self):
        ftsz = 16
        ft = ("Courier", ftsz)
        aftsz = 12
        aft = ("Courier", aftsz)

        self.pen = turtle.RawTurtle(self.screen,shape = "turtle")
        self.pen.color("green")
        self.pen.speed(0)

        query = "SELECT n_name FROM nation, region,supplier WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN (SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA')"
        annotationList = {"r_regionkey=n_regionkey": ["First annotation"],
                  "r_name <> 'AMERICA'": ["Second annotation"], "region": ["Third annotation", "Fourth annotation", "Fifth annotation"]}


        wordList = ['SELECT', 'n_name', 'FROM', 'nation,', 'region', ',supplier', 'WHERE', 'r_regionkey=n_regionkey', 'AND', 's_nationkey', '=', 'n_nationkey', 'AND', 'n_name', 'IN', '(SELECT', 'DISTINCT', 'n_name', 'FROM', 'nation', 'region', 'WHERE', 'r_regionkey=n_regionkey', 'AND', "r_name <> 'AMERICA'", ')', 'AND', 'r_name', 'in', '(SELECT', 'DISTINCT', 'r_name', 'from', 'region', 'where', 'r_name', '<>', "'ASIA')"]
        wordannoidx = [4, 7, 20, 24, 33]

        wheight, wwidth = 604, 1204
        interv = wheight/len(wordannoidx)
        annopos = (1/2) * wheight - 18

        self.pen.penup()
        self.pen.setposition(-(1/2)*wwidth + 5, (1/7)*wheight)
        self.pen.setheading(0)

        for i in range(len(wordList)):  # Iterate through word list
            if wordannoidx and i == wordannoidx[0]:  # HIGHLIGHTING
                self.pen.color("yellow")
                self.pen.pendown()
                self.pen.begin_fill()
                for k in range(2):
                    self.pen.forward(len(wordList[i]) * 14)
                    self.pen.left(90)
                    self.pen.forward(16)
                    self.pen.left(90)
                self.pen.end_fill()
                self.pen.penup()
                self.pen.color("black")
            self.pen.write(wordList[i], font=ft)
            self.pen.forward(len(wordList[i]) * 14)
            # For annotating
            if wordannoidx and i == wordannoidx[0]:  # ANNOTATION FOUND
                # Writing and pointing
                curpos = self.pen.pos()
                self.pen.setheading(90)
                self.pen.forward(16)
                self.pen.setheading(180)
                self.pen.forward(len(wordList[i]) * 0.5*14)
                self.pen.setheading(0)
                self.pen.pendown()
                self.pen.color("blue")
                self.pen.setposition((1/6)*wwidth + 5, annopos)
                self.pen.penup()
                self.pen.color("red")
                annopos -= interv
                # PRINTNG OUT THE ANNOTATIONS
                # print(annotationList[wordList[i]])
                ttext = annotationList[wordList[i]][0]
                # print("Annotation to be printed: " + ttext)
                annotationList[wordList[i]].pop(0)
                annotxtlist = ttext.split()
                # print(annotxtlist)
                for j in range(len(annotxtlist)):
                    self.pen.write(annotxtlist[j], font=aft)
                    self.pen.forward(len(annotxtlist[j])*10 + 5)
                    if (j != (len(annotxtlist)-1)) and (self.pen.pos()[0] + len(annotxtlist[j+1])*10 >= (1/2)*wwidth):
                        self.pen.setheading(270)
                        self.pen.forward(aftsz+5)
                        self.pen.setposition((1/6)*wwidth + 5, self.pen.pos()[1])
                        self.pen.setheading(0)
                self.pen.setposition(curpos)
                self.pen.color("black")
                wordannoidx.pop(0)
            # If next word is not comma
            if i != (len(wordList)-1) and wordList[i+1] != ",":
                self.pen.forward(10)
            if i != (len(wordList)-1):
                tempword = wordList[i+1].lower()
                if "(" in tempword:
                    # print("Bracketed word found:" + tempword)
                    tempword = tempword[1:]
                    # print("Unbracketed: " + tempword)
            if (i != (len(wordList)-1) and tempword in ["select", "from", "where"])\
                    or (i != (len(wordList)-1) and (self.pen.pos()[0] + (len(wordList[i+1]) * 14)) >= (1/6)*wwidth):
                # print("Next line for tempword: " + tempword)
                self.pen.setheading(270)
                self.pen.forward(ftsz+5)
                self.pen.setposition(-(1/2) * wwidth + 5, self.pen.pos()[1])
                self.pen.setheading(0)

    def press(self):
        self.do_stuff()


if __name__ == '__main__':
    root = tk.Tk()
    app = UserInterface(root)

    root.mainloop()


###
# self.screen = turtle.TurtleScreen(self.canvas)
# self.screen.bgcolor("cyan")
# self.button = tk.Button(self.master, text="Press me", command=self.press)
# self.button.pack()
