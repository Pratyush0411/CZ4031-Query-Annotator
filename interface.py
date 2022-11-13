import turtle
import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import *
from tkinter import ttk
import main


class UserInterface:

    font = ("Segoe", 12)

    def __init__(self, master):
        self.canvaswidth = 1600
        self.canvasheight = 800
        self.textwidth = int(0.03*self.canvaswidth)
        self.textheight = int(0.03*self.canvasheight)

        # MASTER WINDOW
        self.master = master
        self.master.title("CZ4031-QUERY-ANNOTATOR")
        # self.master.geometry(str(self.canvaswidth) +
        #                      "x" + str(self.canvasheight))

        # LEFT FRAME
        self.Lframe = tk.Frame(
            self.master, width=self.canvaswidth/2, height=self.canvasheight, bg="GREEN")
        self.Lframe.grid(column=0, row=0)

        # RIGHT FRAME
        self.Rframe = tk.Frame(
            self.master, width=self.canvaswidth/2, height=self.canvasheight, bg="BLUE")
        self.Rframe.grid(column=1, row=0)

        # TURTLE CANVAS
        self.TurtleCanvas = tk.Canvas(
            self.Lframe, width=self.canvaswidth/2, height=self.canvasheight, bg="BLUE")
        self.TurtleCanvas.grid(column=0, row=0)

        # self.canvas = tk.Canvas(master)
        # self.canvas.config(width=self.canvaswidth,
        #                    height=self.canvasheight, bg="blue")
        # self.canvas.pack(side=tk.LEFT)

        # self.canvas.update()
        # print(self.canvas.winfo_reqheight())
        # print(self.canvas.winfo_height())

        # self.innerFrame = Frame(master, width=self.canvas.winfo_width(
        # )/2, height=self.canvas.winfo_height()/2, bg="GREEN")
        # # self.innerFrame.pack()

        # self.canvas.create_window(400, 400, window=self.innerFrame)

        # self.turtlecanvas = tk.Canvas(
        #     self.innerFrame, width=100, height=20, bg="RED")
        # self.turtlecanvas.config(bg="RED", width=self.canvas.winfo_width(
        # )/2, height=self.canvas.winfo_height()/2)
        # self.turtlecanvas.pack()

        # scrollbar = Scrollbar()
        # self.textfield = tk.Text(root, height = 20, width = 40, font= ("Segoe",12), yscrollcommand= scrollbar.set)
        # scrollbar.config(command = self.textfield.yview)
        # scrollbar.pack(side = RIGHT, fill = Y)

        self.textfield = st.ScrolledText(
            self.Rframe, height=self.textheight, width=self.textwidth, font=self.font)
        self.sendQueryButton = tk.Button(
            self.Rframe, text="Send Query", command=self.get_input)
        self.clearInputButton = tk.Button(
            self.Rframe, text="Clear input", command=self.clear_input)
        self.clearScreenButton = tk.Button(
            self.Rframe, text="Clear screen", command=self.clear_screen)

        self.progressLabel = tk.Label(
            self.Rframe, text="RUNNING OPTIMIZER... PLEASE WAIT")
        self.progressLabel.config(font=self.font, bg="GREEN", fg="WHITE")

        self.errorLabel = tk.Label(
            self.Rframe, text="PLEASE INPUT AN APPROPRIATE SQL QUERY")
        self.errorLabel.config(font=self.font, bg="RED", fg="WHITE")

        self.label = tk.Label(
            self.Rframe, text="Enter your query to optimize: ")
        self.label.config(font=self.font)

        self.label.grid(column=0, row=0)
        self.textfield.grid(column=0, row=1)
        self.sendQueryButton.grid(column=0, row=2)
        self.clearInputButton.grid(column=0, row=3)
        self.clearScreenButton.grid(column=0, row=4)
        # self.sendQueryButton.pack()
        # self.cancelButton.pack(side = tk.RIGHT)

        self.screen = turtle.TurtleScreen(self.TurtleCanvas)
        self.screen.bgcolor("YELLOW")

    def clear_input(self):
        self.textfield.delete("1.0", "end")

    def clear_screen(self):
        self.screen.clearscreen()

    def show_progressBar(self):
        print("======================== SHOWING PROGRESS BAR ========================")
        self.progressLabel.pack(side=tk.BOTTOM)
        # self.progressBar.pack(side = tk.BOTTOM)
        # self.progressBar.start()

    def hide_progressBar(self):
        print("======================== HIDING PROGRESS BAR ========================")
        self.progressLabel.pack_forget()
        # self.progressBar.stop()
        # self.progressBar.pack_forget()

    def show_errorLabel(self):
        self.errorLabel.pack(side=tk.BOTTOM)

    def hide_errorLabel(self):
        self.errorLabel.pack_forget()

    def get_input(self):
        self.clear_screen()
        query = self.textfield.get("1.0", "end")

        print("======================== RETRIEVED QUERY: ========================", '\n', query)
        print("======================== RUNNING ALGORITHM... ========================")
        try:
            self.hide_errorLabel
            ans, cleaned_query = main.main(query)
        except:
            self.show_errorLabel()

        if ans == {}:
            self.show_errorLabel()

        print("======================== CLEANED QUERY: ========================",
              '\n', cleaned_query)
        print("======================== DICTIONARY: ========================", '\n',  ans)
        self.TurtleCanvas.update()
        print("Turtle canvas width: ", self.TurtleCanvas.winfo_width())
        print("Turtle canvas height: ", self.TurtleCanvas.winfo_height())
        self.instance = Annotator(
            cleaned_query, ans, self.TurtleCanvas.winfo_height(), self.TurtleCanvas.winfo_width())
        wordannoidx, wordList = Annotator.annotation_matcher(self.instance)
        print(
            "======================== WORD LIST: ========================", '\n', wordList)
        print("======================== ANNOTATION INDEX: ========================",
              '\n', wordannoidx)
        self.hide_progressBar()
        print("======================== BEGINNING DRAWING ========================")
        Annotator.turtle_drawer(self, wordannoidx, wordList, ans,
                                self.TurtleCanvas.winfo_height(), self.TurtleCanvas.winfo_width())


class Annotator:
    def __init__(self, query, annotationList, height, width):
        self.annotationList = annotationList
        self.query = query
        self.aheight = height
        self.awidth = width

    def annotation_matcher(self):
        # Pre-processing of query in order to return the indexes of the annotee
        tquery = self.query
        specList = ["(", ")", " ", ",", "\0"]
        idsort = []
        annoidx = {}  # "annotee index number" : "annotee"

        # 1) Sort the annotatees by increasing length
        keyList = list(self.annotationList.keys())
        keyList.sort(key=len, reverse=True)
        # print("1) Annotees sorted: " + str(keyList))
        # print()

        # 2) Iterate through the annotees by the number of annotations they have in their array.
        #    Identify the indexes of the annotees, checking that they do not overlap with previous ones
        #    For each annotee, check that the left and write of it are either a space, comma, or bracket, and not other letters
        for k in keyList:
            # print("Finding indexes for " + k)
            if type(self.annotationList[k]) == list:  # If the value is a list
                print("Value is a list")
                count = len(self.annotationList[k])
            else:
                count = 1
            # print("Start count: " + str(count))
            strt = 0
            while count > 0:  # While there are still instances of k not found yet
                # print("COUNT:", count)
                # print("Count: " + str(count))
                # Find first occurence of key k
                # print(tquery)
                tindex = tquery.find(k, strt, len(tquery))
                # print(tindex)
                # Check if actually the annotee, not part of bigger word
                # If the found word is surrounded by letters
                if tquery[tindex-1] not in specList or (tindex + len(k) < len(tquery) and (tquery[tindex + len(k)] not in specList)):
                    # print("A")
                    # Set the next loop to start the find after this occurence
                    strt = tindex + len(k)
                    continue  # go to next loop
                else:  # Means that proper occurence was found
                    # print("B")
                    # Append the index of k to the idsort list
                    idsort.append(tindex)
                    annoidx[tindex] = k  # Add the index to the dictionary
                    tquery = tquery[:tindex] + " " * \
                        len(k) + tquery[(tindex+len(k)):]
                    count -= 1  # Reduce count by 1
        idsort.sort()
        # print("Indexes of annotees in query found:")
        # print(idsort)
        # print(annoidx)
        # print()

        # 3) Iterate through the annotation indexes and split the query into words accordingly.
        #    Record the indexes of the words with annotations, to be detected later during printing
        wordList = []  # List of words in the query
        wordannoidx = []  # List of the indexes of annotated words based on the word list
        idx = 0
        tquery = self.query

        for tid in idsort:
            if tquery[idx:tid-1]:
                tlist = tquery[idx:tid-1].split()
                wordList.extend(tlist)
            wordList.append(annoidx[tid])
            wordannoidx.append(len(wordList)-1)
            idx = tid + len(annoidx[tid])

        tlist = tquery[idx:].split()
        wordList.extend(tlist)

        # print("Word list created, indexes of annotees identified")
        # print("Word list: " + str(wordList))
        # print("Annotee indexes: " + str(wordannoidx))
        # print()

        return wordannoidx, wordList

    def turtle_drawer(self, wordannoidx, wordList, annotationList, aheight, awidth):

        ftsz = 10
        ft = ("Segoe", ftsz)
        aftsz = 8
        aft = ("Segoe", aftsz)
        annodiv = 0

        self.pen = turtle.RawTurtle(self.screen, shape="turtle")
        self.pen.color("green")
        self.pen.speed(0)

        wheight, wwidth = aheight, awidth
        interv = wheight/len(wordannoidx)
        annopos = (1/2) * wheight - 18

        self.pen.penup()
        self.pen.setposition(-(1/2)*wwidth + 5, (1/3)*wheight-ftsz)
        self.pen.setheading(0)

        for i in range(len(wordList)):  # Iterate through word list
            if wordannoidx and i == wordannoidx[0]:  # HIGHLIGHTING
                self.pen.color("yellow")
                self.pen.pendown()
                self.pen.begin_fill()
                for k in range(2):
                    self.pen.forward(len(wordList[i]) * (ftsz-3))
                    self.pen.left(90)
                    self.pen.forward(16)
                    self.pen.left(90)
                self.pen.end_fill()
                self.pen.penup()
                self.pen.color("black")
            # NORMAL WRITING
            self.pen.write(wordList[i], font=ft)
            self.pen.forward(len(wordList[i]) * ftsz)
            # For annotating
            if wordannoidx and i == wordannoidx[0]:  # ANNOTATION FOUND
                # Writing and pointing
                curpos = self.pen.pos()
                self.pen.setheading(90)
                self.pen.forward(16)
                self.pen.setheading(180)
                self.pen.forward(len(wordList[i]) * 0.5 * ftsz)
                self.pen.setheading(0)
                self.pen.pendown()
                self.pen.color("blue")
                self.pen.setposition((annodiv)*wwidth + 5, annopos)
                self.pen.penup()
                self.pen.color("red")
                # annopos -= interv
                # PRINTNG OUT THE ANNOTATIONS

                # print(annotationList[wordList[i]])
                # print("Annotation to be printed: " + ttext)
                if type(annotationList[wordList[i]]) == list:
                    ttext = annotationList[wordList[i]][0]
                    annotationList[wordList[i]].pop(0)
                else:
                    ttext = annotationList[wordList[i]]
                annotxtlist = ttext.split()
                # print(annotxtlist)
                for j in range(len(annotxtlist)):
                    self.pen.write(annotxtlist[j], font=aft)
                    self.pen.forward(len(annotxtlist[j])*aftsz)
                    if (j != (len(annotxtlist)-1)) and (self.pen.pos()[0] + len(annotxtlist[j+1])*10 >= (1/2)*wwidth):
                        self.pen.setheading(270)
                        self.pen.forward(aftsz+5)
                        self.pen.setposition(
                            (annodiv)*wwidth + 5, self.pen.pos()[1])
                        self.pen.setheading(0)
                annopos = self.pen.pos()[1] - aftsz - 7
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
                    or (i != (len(wordList)-1) and (self.pen.pos()[0] + (len(wordList[i+1]) * 14)) >= (annodiv)*wwidth):
                # print("Next line for tempword: " + tempword)
                self.pen.setheading(270)
                self.pen.forward(ftsz+5)
                self.pen.setposition(-(1/2) * wwidth + 5, self.pen.pos()[1])
                self.pen.setheading(0)

        self.pen.setposition(wwidth, wheight)
        # turtle.done
        # print("Turtle finished")
        # window.exitonclick()

        # turtle.done


if __name__ == '__main__':
    root = tk.Tk()
    app = UserInterface(root)

    root.mainloop()
