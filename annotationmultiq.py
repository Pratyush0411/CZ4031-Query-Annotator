# Import libraries
import turtle

# Input data

# # query = "select * from customer C, orders O where C.c_custkey = O.o_custkey and A = B"
# annotationList = {"customer C": ["This is the first annotation"],
#                   "C.c_custkey = O.o_custkey": ["This is the second annotation that is a bit longer than the other ones and spans more than one line"],
#                   "A = B": ["This is the third annotation"], "orders O": ["This is the 4th one"]}

# query = "SELECT n_name FROM nation, region,supplier WHERE r_regionkey=n_regionkey AND s_nationkey = n_nationkey AND n_name IN (SELECT DISTINCT n_name FROM nation,region WHERE r_regionkey=n_regionkey AND r_name <> 'AMERICA') AND r_name in (SELECT DISTINCT r_name from region where r_name <> 'ASIA')"
# annotationList = {"r_regionkey=n_regionkey": "First annotation",
#                   "r_name <> 'AMERICA'": ["Second annotation"], "region": ["Third annotation", "Fourth annotation", "Fifth annotation"]}

# query = "select * from part where p_brand = 'Brand#13' and p_size <> (select max(p_size) from part);"
# annotationList = {"part": ["This is the annotation for the part in the outer query",
#                            "This is the annotation for the part in the nested subquery"], "p_brand": ["This is the annotation for p_brand"]}

from db import DBConnection
class Annotator:
    def __init__(self,query, annotationList):
        self.annotationList = annotationList
        self.query = query
    
    def annotation_matcher(self):
        # Pre-processing of query in order to return the indexes of the annotee
        tquery = self.query
        specList = ["(", ")", " ", ",", "\0"]
        idsort = []
        annoidx = {}  # "annotee index number" : "annotee"

        # 1) Sort the annotatees by increasing length
        keyList = list(self.annotationList.keys())
        keyList.sort(key=len, reverse=True)
        print("1) Annotees sorted: " + str(keyList))
        print()


        # 2) Iterate through the annotees by the number of annotations they have in their array.
        #    Identify the indexes of the annotees, checking that they do not overlap with previous ones
        #    For each annotee, check that the left and write of it are either a space, comma, or bracket, and not other letters
        for k in keyList:
            # print("Finding indexes for " + k)
            if type(self.annotationList[k]) == list: # If the value is a list
                count = len(self.annotationList[k])
            else:
                count = 1
            # print("Start count: " + str(count))
            strt = 0
            while count > 0:  # While there are still instances of k not found yet
                # print("Count: " + str(count))
                # Find first occurence of key k
                print(tquery)
                tindex = tquery.find(k, strt, len(tquery))
                print(tindex)
                # Check if actually the annotee, not part of bigger word
                # If the found word is surrounded by letters
                if tquery[tindex-1] not in specList or (tindex + len(k) < len(tquery) and (tquery[tindex + len(k)] not in specList)):
                    # Set the next loop to start the find after this occurence
                    strt = tindex + len(k)
                    continue  # go to next loop
                else:  # Means that proper occurence was found
                    idsort.append(tindex)  # Append the index of k to the idsort list
                    annoidx[tindex] = k  # Add the index to the dictionary
                    tquery = tquery[:tindex] + " " * len(k) + tquery[(tindex+len(k)):]
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
    
    def turtle_drawer(self, wordannoidx, wordList, annotationList):

        ftsz = 16
        ft = ("Courier", ftsz)
        aftsz = 12
        aft = ("Courier", aftsz)

        self.pen = turtle.RawTurtle(self.screen,shape = "turtle")
        self.pen.color("green")
        self.pen.speed(0)

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

        # pen.setposition(wwidth, wheight)
        # print("Turtle finished")
        # window.exitonclick()

        # turtle.done
