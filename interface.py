import turtle
import tkinter as tk
import tkinter.scrolledtext as st
from tkinter import *
import annotation

class UserInterface: # MAIN USER INTERFACE CLASS
    font = ("Segoe", 12)

    def __init__(self, master):
        self.canvaswidth = 1600
        self.canvasheight = 800
        self.textwidth = int(0.03*self.canvaswidth)
        self.textheight = int(0.03*self.canvasheight)

        # MASTER WINDOW
        self.master = master
        self.master.title("CZ4031-QUERY-ANNOTATOR")

        # LEFT FRAME
        self.Lframe = tk.Frame(
            self.master, width=self.canvaswidth/2, height=self.canvasheight)
        self.Lframe.grid(column=0, row=0)

        # RIGHT FRAME
        self.Rframe = tk.Frame(
            self.master, width=self.canvaswidth/2, height=self.canvasheight)
        self.Rframe.grid(column=1, row=0)
    
        # TURTLE CANVAS IN LEFT FRAME
        self.TurtleCanvas = tk.Canvas(
            self.Lframe, width=self.canvaswidth/2, height=self.canvasheight)
        self.TurtleCanvas.grid(column=0, row=0)

        self.screen = turtle.TurtleScreen(self.TurtleCanvas)
        self.screen.bgcolor("WHITE")

        # SCROLLBAR FOR TURTLE CANVAS
        self.scrollbar = Scrollbar(self.Lframe, orient = 'vertical' )
        self.scrollbar.config(command = self.TurtleCanvas.yview) 
        self.TurtleCanvas.config(yscrollcommand= self.scrollbar.set)
        self.scrollbar.grid(column = 1, row = 0, sticky = N+S+W)

        # CREATING USER INPUT COMPONENTS AND PLACING THEM INTO RIGHT FRAME
        self.textfield = st.ScrolledText(self.Rframe, height=self.textheight, width=self.textwidth, font=self.font)
        self.sendQueryButton = tk.Button(self.Rframe, text="Send Query", command= lambda: self.get_input())
        self.clearInputButton = tk.Button(self.Rframe, text="Clear input", command= lambda: self.clear_input())
        self.clearScreenButton = tk.Button(self.Rframe, text="Clear screen", command= lambda: self.clear_screen())

        self.progressLabel = tk.Label(self.Rframe, text="RUNNING OPTIMIZER... PLEASE WAIT")
        self.progressLabel.config(font=self.font, bg="GREEN", fg="WHITE")

        self.errorLabel = tk.Label(self.Rframe, text="PLEASE INPUT AN APPROPRIATE SQL QUERY")
        self.errorLabel.config(font=self.font, bg="RED", fg="WHITE")

        self.label = tk.Label(self.Rframe, text="Enter your query to annotate: ")
        self.label.config(font=self.font)

        self.label.grid(column=0, row=0)
        self.textfield.grid(column=0, row=1)
        self.sendQueryButton.grid(column=0, row=2)
        self.clearInputButton.grid(column=0, row=3)
        self.clearScreenButton.grid(column=0, row=4)

        self.buttonFrame = tk.Frame(self.Rframe)
        self.buttonFrame.grid(column = 0, row = 6, pady = 15)

        self.queryOneButton = tk.Button(self.buttonFrame, text = "Query 1", command = lambda: self.send_query(1)).grid(column = 0, row = 0, padx = 10)
        self.queryTwoButton = tk.Button(self.buttonFrame, text = "Query 2", command = lambda: self.send_query(2)).grid(column = 1, row = 0, padx = 10)
        self.queryThreeButton = tk.Button(self.buttonFrame, text = "Query 3", command = lambda: self.send_query(3)).grid(column = 2, row = 0, padx = 10)
        self.queryFourButton = tk.Button(self.buttonFrame, text = "Query 4", command = lambda: self.send_query(4)).grid(column = 0, row = 1, padx = 10, pady = 10)
        self.queryFiveButton = tk.Button(self.buttonFrame, text = "Query 5", command = lambda: self.send_query(5)).grid(column = 1, row = 1, padx = 10, pady = 10)
        self.querySixButton = tk.Button(self.buttonFrame, text = "Query 6", command = lambda: self.send_query(6)).grid(column = 2, row = 1, padx = 10, pady = 10)


    def send_query(self,number): # FUNCTION USED FOR THE PRE-DEFINED QUERY 1-6 BUTTONS
        if number == 1:
            self.clear_input()
            self.textfield.insert(END,q1)
        elif number == 2:
            self.clear_input()
            self.textfield.insert(END,q2)
        elif number == 3:
            self.clear_input()
            self.textfield.insert(END,q3)
        elif number == 4:
            self.clear_input()
            self.textfield.insert(END,q4)
        elif number == 5:
            self.clear_input()
            self.textfield.insert(END,q5)
        elif number == 6:
            self.clear_input()
            self.textfield.insert(END,q6)

    def clear_input(self): # FUNCTION USED TO CLEAR THE TEXTFIELD INPUT
        self.textfield.delete("1.0", "end")

    def clear_screen(self): # FUNCTION USED TO CLEAR THE TURTLE CANVAS SCREEN
        self.screen.clearscreen()

    def show_progressLabel(self): # FUNCTION USED TO SHOW PROGRESS LABEL WHEN A QUERY IS SENT
        print("======================== SHOWING PROGRESS LABEL ========================")
        self.progressLabel.grid(column = 0, row = 7)

    def hide_progressLabel(self): # FUNCTION USED TO HIDE PROGRESS LABEL
        print("======================== HIDING PROGRESS LABEL ========================")
        self.progressLabel.grid_remove()

    def show_errorLabel(self): # FUNCTION USED TO SHOW ERROR LABEL WHEN A QUERY SENT IS INCORRECT / SYNTAX ERROR / RETURN NULL
        print("======================== SHOWING ERROR LABEL ========================")
        self.errorLabel.grid(column = 0, row = 7)

    def hide_errorLabel(self): # FUNCTION USED TO HIDE ERROR LABEL
        print("======================== HIDING ERROR LABEL ========================")
        self.errorLabel.grid_remove()

    def get_input(self): # MAIN FUNCTION INVOKED WHEN SEND QUERY BUTTON IS PRESSED, QUERY IS SENT FOR PREPROCESSING AND ANNOTATION.
        self.show_progressLabel()
        try:
            self.errorLabel.grid_remove()
        except:
            pass

        # CLEAR SCREEN BEFORE STARTING ANY NEW DRAWINGS
        self.clear_screen()
        # OBTAIN QUERY FROM TEXTFIELD
        query = self.textfield.get("1.0", "end")

        print("======================== RETRIEVED QUERY: ========================", '\n', query)
        print("======================== RUNNING ALGORITHM... ========================")
        
        # TRY-EXCEPT CLAUSE FOR INCORRECT QUERIES
        try:
            ans, cleaned_query = annotation.annotator(query)
        except:
            self.hide_progressLabel()
            self.show_errorLabel()

        if ans == {}:
            self.hide_progressLabel()
            self.show_errorLabel()

        print("======================== CLEANED QUERY: ========================",'\n', cleaned_query)
        print("======================== DICTIONARY: ========================", '\n',  ans)

        self.TurtleCanvas.update()
        print("Turtle canvas width: ", self.TurtleCanvas.winfo_width())
        print("Turtle canvas height: ", self.TurtleCanvas.winfo_height())

        # OBTAINING ANNOTATION LIST FROM ANNOTATOR CLASS
        self.instance = Annotator(cleaned_query, ans, self.TurtleCanvas.winfo_height(), self.TurtleCanvas.winfo_width())
        wordannoidx, wordList = Annotator.annotation_matcher(self.instance)

        print("======================== WORD LIST: ========================", '\n', wordList)
        print("======================== ANNOTATION INDEX: ========================",'\n', wordannoidx)

        # HIDE PROGRESS LABEL ONCE ALL RESULTS ARE OBTAINED.
        self.hide_progressLabel()

        print("======================== BEGINNING DRAWING ========================")
        Annotator.turtle_drawer(self, wordannoidx, wordList, ans, self.TurtleCanvas.winfo_height(), self.TurtleCanvas.winfo_width())
        print("======================== DRAWING FINISHED ========================")



class Annotator: # CLASS USED TO PROCESS THE RESULTS OBTAINED FROM THE ALGORITHMS
    def __init__(self, query, annotationList, height, width):
        self.annotationList = annotationList
        self.query = query
        self.aheight = height
        self.awidth = width

    def annotation_matcher(self):
        # Pre-processing of query in order to return the indexes of the annotee
        tquery = self.query
        specList = ["(", ")", " ", ",", ';', "\0"]
        idsort = []
        annoidx = {}  # "annotee index number" : "annotee"

        # 1) Sort the annotatees by increasing length
        keyList = list(self.annotationList.keys())
        keyList.sort(key=len, reverse=True)

        # 2) Iterate through the annotees by the number of annotations they have in their array.
        #    Identify the indexes of the annotees, checking that they do not overlap with previous ones
        #    For each annotee, check that the left and write of it are either a space, comma, or bracket, and not other letters
        for k in keyList:
            if type(self.annotationList[k]) == list:  # If the value is a list
                count = len(self.annotationList[k])
            else:
                count = 1
            strt = 0
            while count > 0:  # While there are still instances of k not found yet
                # Find first occurence of key k
                tindex = tquery.find(k, strt, len(tquery))
                # Check if actually the annotee, not part of bigger word
                # If the found word is surrounded by letters
                if tquery[tindex-1] not in specList or (tindex + len(k) < len(tquery) and (tquery[tindex + len(k)] not in specList)):
                    # Set the next loop to start the find after this occurence
                    strt = tindex + len(k)
                    continue  # go to next loop
                else:  # Means that proper occurence was found
                    # Append the index of k to the idsort list
                    idsort.append(tindex)
                    annoidx[tindex] = k  # Add the index to the dictionary
                    tquery = tquery[:tindex] + " " * \
                        len(k) + tquery[(tindex+len(k)):]
                    count -= 1  # Reduce count by 1
        idsort.sort()
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

        return wordannoidx, wordList

    def turtle_drawer(self, wordannoidx, wordList, annotationList, aheight, awidth): # BEGIN DRAWING BASED ON ANNOTATION INDEXES
        ftsz = 12
        ft = ("Segoe", ftsz)
        aftsz = 10
        aft = ("Segoe", aftsz)
        annodiv = 0

        self.pen = turtle.RawTurtle(self.screen, shape="turtle")
        self.pen.color("black")
        self.pen.speed(0)

        wheight, wwidth = aheight, awidth
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
                self.pen.forward(8)
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
                if type(annotationList[wordList[i]]) == list:
                    ttext = annotationList[wordList[i]][0]
                    annotationList[wordList[i]].pop(0)
                else:
                    ttext = annotationList[wordList[i]]
                annotxtlist = ttext.split()
                for j in range(len(annotxtlist)):
                    self.pen.write(annotxtlist[j], font=aft)
                    self.pen.forward(len(annotxtlist[j])*aftsz)
                    if (j != (len(annotxtlist)-1)) and (self.pen.pos()[0] + len(annotxtlist[j+1])*10 >= (1/2)*wwidth):
                        self.pen.setheading(270)
                        self.pen.forward(aftsz+5)
                        self.pen.setposition(
                            (annodiv)*wwidth + 5, self.pen.pos()[1])
                        self.pen.setheading(0)
                        self.TurtleCanvas.configure(scrollregion=self.TurtleCanvas.bbox("all")) # TO UPDATE THE TURTLECANVAS SO THAT SCROLLBAR IS UPDATED
                annopos = self.pen.pos()[1] - aftsz - 50
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

q1 = """SELECT n_name
FROM nation N, region R,supplier S
WHERE R.r_regionkey=N.n_regionkey AND S.s_nationkey = N.n_nationkey AND N.n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');"""

q2 = """ select * from part where p_brand = 'Brand#13' and p_size <> (select max(p_size) from part);"""

q3 = """SELECT n_name
FROM nation, region,supplier
WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN 
(SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA' AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'LATIN AMERICA' AND r_name <> 'AFRICA')) AND
r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA');"""

q4 = '''select
      n_name,
      sum(l_extendedprice * (1 - l_discount)) as revenue
    from
      customer,
      orders,
      lineitem,
      supplier,
      nation,
      region
    where
      c_custkey = o_custkey
      and l_orderkey = o_orderkey
      and l_suppkey = s_suppkey
      and c_nationkey = s_nationkey
      and s_nationkey = n_nationkey
      and n_regionkey = r_regionkey
      and r_name = 'ASIA'
      and o_orderdate >= '1994-01-01'
      and o_orderdate < '1995-01-01'
      and c_acctbal > 10
      and s_acctbal > 20
    group by
      n_name
    order by
      revenue desc;
'''

q5 = '''select
      supp_nation,
      cust_nation,
      l_year,
      sum(volume) as revenue
    from
      (
        select
          n1.n_name as supp_nation,
          n2.n_name as cust_nation,
          DATE_PART('YEAR',l_shipdate) as l_year,
          l_extendedprice * (1 - l_discount) as volume
        from
          supplier,
          lineitem,
          orders,
          customer,
          nation n1,
          nation n2
        where
          s_suppkey = l_suppkey
          and o_orderkey = l_orderkey
          and c_custkey = o_custkey
          and s_nationkey = n1.n_nationkey
          and c_nationkey = n2.n_nationkey
          and (
            (n1.n_name = 'FRANCE' and n2.n_name = 'GERMANY')
            or (n1.n_name = 'GERMANY' and n2.n_name = 'FRANCE')
          )
          and l_shipdate >= '1995-01-01' 
          and o_totalprice > 100
          and c_acctbal > 10
      ) as shipping
    group by
      supp_nation,
      cust_nation,
      l_year
    order by
      supp_nation,
      cust_nation,
      l_year;

'''

q6 = '''select
	sum(l_extendedprice) / 7.0 as avg_yearly
from
	lineitem,
	part,
        (select l_partkey as agg_partkey, 0.2 * avg(l_quantity) as avg_quantity from lineitem group by l_partkey) part_agg
where
	p_partkey = l_partkey
        and agg_partkey = l_partkey
	and p_brand = 'brand#33'
	and p_container = 'wrap jar'
	and l_quantity < avg_quantity  
limit 1;
'''
