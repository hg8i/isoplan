from __future__ import division
import math, sys, time, copy
import curses
import logging
import numpy as np
import datetime




"""
Calendar grid: draws calendar view in provided window
"""

def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()

class calendarView:
    def __init__(self,window,setup,backend):
        self._setup = setup
        self._backend = backend
        self._window = window
        self._focus = setup["focus"]
        self._weekLow = setup["weekLow"]
        self._weekHigh = setup["weekHigh"]
        self._nX = 7
        self._nY = self._weekHigh+self._weekLow+1
        self._headerHeight = 3
        self._siderWidth = 4
        self._content = {}
        self._loadData()
        # options
        self._optionWeeksVert = False
        # self._optionFocusChar = curses.ACS_CKBOARD
        self._optionFocusChar = " "

        # highlight color
        self._optionYearColor          = setup["colors"]["year"]
        self._optionMonthColor         = setup["colors"]["month"]
        self._optionContentSelectColor = setup["highlights"]["select"]
        self._optionRegularColor       = setup["colors"]["default"]
        self._optionFocusColor         = setup["highlights"]["focus"]
        self._optionTodayColor         = setup["colors"]["focus"]



        self._dayName=["Workday {0}".format(i) for i in range(self._nX)]
        self._dayName[0] = "Extraworkdaytoday"
        self._dayName=setup["dayNames"]

        self._monthName=setup["monthNames"]
        self._clearWindow()
        self.update()

        # window.border()
        # window.refresh()

    def _clearWindow(self):
        """ Write blanks to window to clear """
        boxColor = self._optionRegularColor
        self._screenY,self._screenX = self._window.getmaxyx()
        self._drawBox(0,0,self._screenY,self._screenX,self._optionFocusChar,boxColor)


    def _loadData(self):
        """ Load/update new data """

        weekLow,weekHigh = self._weekLow,self._weekHigh
        backend = self._backend
        weekData = []
        for i in range(-weekLow,weekHigh+1):
            weekData.append(backend.getWeekNumber(offset=i))

        self._weekNumbers  = [w["week"] for w in weekData]
        self._yearNumbers  = [w["year"] for w in weekData]
        self._monthNumbers = [w["month"] for w in weekData]

        # for weekNumber in self._weekNumbers

        for i in range(-weekLow,weekHigh+1):
            days = backend.getWeek(offset=i)
            for iDay,day in enumerate(days):
                self._loadDayContent(day)



    def update(self,window=None,depth=0):
        """ Update calendar view """
        if window==None: window = self._window
        if depth==1:
            raise BaseException("Something is going wrong with the calendar view update")
        self._window = window
        # available window
        self._screenY,self._screenX = self._window.getmaxyx()
        # cell width
        self._cellL = int(math.floor((self._screenX-1-self._siderWidth)/self._nX))
        self._cellH = int(math.floor((self._screenY-1-self._headerHeight)/self._nY))
        # centering offset
        self._offsetX = self._siderWidth + math.floor((self._screenX-self._siderWidth-(self._cellL*self._nX))/2)
        self._offsetY = self._headerHeight + math.floor((self._screenY-self._headerHeight-(self._cellH*self._nY))/2)
        # points for grid
        # try:
        if 1:
            self._drawGrid()
            self._drawHeader()
            self._drawSider()
            self._drawAllContent()
            # self._drawDiagnostics()
        # except:
        #     self._move(0,0)
        #     # wait (terminal may be resizing)
        #     _print("ERROR: retrying update soon")
        #     self.update(depth=depth+1)

    def _hline(self,y,x,l,char=None,color=0):
        if char==None: char = curses.ACS_HLINE
        self._move(int(y),int(x))
        try:
            self._window.hline(char,int(l),curses.color_pair(color))
        except:
            _print("Failed while drawing")

    def _vline(self,y,x,l,color=0):
        self._move(int(y),int(x))
        try:
            self._window.vline(curses.ACS_VLINE,int(l),curses.color_pair(color))
        except:
            _print("Failed while drawing")

    def _point(self,y,x,c,color=0):
        self._move(int(y),int(x))
        try:
            self._window.addch(c,curses.color_pair(color))
        except:
            _print("Failed while drawing")

    def _move(self,y,x):
        try:
            self._window.move(int(y),int(x))
        except:
            raise BaseException("Failed moving x={0}, y={1}".format(x,y))

    def _text(self,y,x,s,color=0):
        self._move(int(y),int(x))
        try:
            label=str(s)
            self._window.addstr(label,curses.color_pair(color))
        except:
            label=repr(s)
            self._window.addstr(label,curses.color_pair(color))

    def _drawBox(self,y,x,h,l,char,color):
        """ Draw rectangle filled with shaded character """
        # for yPos in range(int(y),int(y+h)):
        for line in range(h):
            self._hline(y+line,x,l,char,color=color)

    def _getGridPoints(self):
        """ Get corners of grid """
        locsX = [self._cellL*i+self._offsetX for i in range(self._nX+1)]
        locsY = [self._cellH*i+self._offsetY for i in range(self._nY+1)]
        return locsY,locsX

    def _drawSider(self):
        """ Draw header, must not exceed the "_headerHeight" variable
        """
        # clear sider 
        boxColor = self._optionRegularColor
        self._drawBox(0,0,self._screenY,self._siderWidth,self._optionFocusChar,boxColor)

        locsY,locsX = self._getGridPoints()
        months= self._monthNumbers
        years = self._yearNumbers
        weeks = self._weekNumbers
        # draw text
        for yi,y in enumerate(locsY[:-1]):
            # week labels
            label = str(weeks[yi])
            if self._optionWeeksVert:
                for i in range(len(label)):
                    self._point(y+i+1,locsX[0]-1,label[i])
            else:
                self._text(y+1,locsX[0]-len(label),label[:2])
            # month labels
            if months[yi]!=months[(yi-1)%len(months)] or yi==0:
                label = self._monthName[months[yi]]
                for i in range(len(label)):
                    if y+i+2>=self._screenY: break
                    self._point(y+i+2,locsX[0]-3,label[i],color=self._optionMonthColor)
            # year labels
            if years[yi]!=years[(yi-1)%len(years)]:
                label = str(years[yi])
                for i in range(len(label)):
                    if y+i+2>=self._screenY: break
                    self._point(y+i+2,locsX[0]-4,label[i],color=self._optionYearColor)


    def _drawHeader(self):
        """ Draw header, must not exceed the "_headerHeight" variable
        """
        locsY,locsX = self._getGridPoints()
        # draw text
        for xi,x in enumerate(locsX[:-1]):
            label = self._dayName[xi][:self._cellL-1]
            # center
            x+=1
            x+=math.floor((self._cellL-len(label))/2)
            self._text(locsY[0]-1,x,label)
        # draw lines
        for xi,x in enumerate(locsX):
            self._point(locsY[0]-1,x,curses.ACS_VLINE)
            self._point(locsY[0],x,curses.ACS_PLUS)
        self._point(locsY[0],locsX[0],curses.ACS_LTEE)
        self._point(locsY[0],locsX[-1],curses.ACS_RTEE)
        self._hline(locsY[0]-2,locsX[0]+1,self._cellL*self._nX-1)

        self._point(locsY[0]-2,locsX[0],curses.ACS_ULCORNER)
        self._point(locsY[0]-2,locsX[-1],curses.ACS_URCORNER)

    def _drawGrid(self):
        """ Draw grid """
        locsY,locsX = self._getGridPoints()

        # draw edges
        for xi,x in enumerate(locsX):
            self._vline(locsY[0]+1,x,self._cellH*self._nY-1)
        for yi,y in enumerate(locsY):
            self._hline(y,locsX[0]+1,self._cellL*self._nX-1)

        # draw rectangle corners
        for xi,x in enumerate(locsX):
            for yi,y in enumerate(locsY):
                # draw rect corners
                if xi==0 and yi==0: 
                    self._point(y,x,curses.ACS_ULCORNER)
                elif xi==len(locsX)-1 and yi==len(locsY)-1: 
                    self._point(y,x,curses.ACS_LRCORNER)
                elif xi==0 and yi==len(locsY)-1: 
                    self._point(y,x,curses.ACS_LLCORNER)
                elif xi==len(locsX)-1 and yi==0: 
                    self._point(y,x,curses.ACS_URCORNER)
                elif xi==0:
                    self._point(y,x,curses.ACS_LTEE)
                elif xi==len(locsX)-1: 
                    self._point(y,x,curses.ACS_RTEE)
                elif yi==0:
                    self._point(y,x,curses.ACS_TTEE)
                elif yi==len(locsY)-1: 
                    self._point(y,x,curses.ACS_BTEE)
                else:
                    self._point(y,x,curses.ACS_PLUS)

    def _getDateContent(self,week,day):
        """ Safely retrieve day's content list, or make a new one """
        if week not in self._content.keys(): self._content[week]={}
        if day not in self._content[week].keys(): self._content[week][day]=[]
        return self._content[week][day]



    def _drawAllContent(self):
        """ Draw all content """
        for week in self._content.keys():
            for day in self._content[week].keys():
                self._drawDayContent(week,day)



    def _drawDayContent(self,week=0,day=0):
        """ Draw day's content from _content 
            week is week number, day is 0-6
        """
        locsY,locsX = self._getGridPoints()

        # content for this box
        content = self._getDateContent(week,day)["content"]
        date = self._getDateContent(week,day)["date"]
        rowNumber = self._weekNumbers.index(week)
        colNumber = day
        eventIndex = self._backend.getEventIndex()
        focusedDay = self._backend.today().weekday()
        focusedWeek = self._backend.toweek()
        dayNumber = str(date.day)
        setup = self._setup
        # if box in focus, highlight
        inFocus = focusedWeek==week and focusedDay==day
        # _print(focusedWeek,week,focusedDay,day)
        boxColor = self._optionRegularColor
        if inFocus:
            boxColor = self._optionContentSelectColor
        self._drawBox(locsY[rowNumber]+1,locsX[colNumber]+1,self._cellH-1,self._cellL-1,self._optionFocusChar,boxColor)
        # make little point indicating "today"
        if date == self._backend.now():
            color = self._optionContentSelectColor if inFocus else self._optionTodayColor
            self._point(locsY[rowNumber]+1,locsX[colNumber]+self._cellL-1,curses.ACS_DIAMOND,color=color)
        self._text(locsY[rowNumber]+1,locsX[colNumber]+1,dayNumber,color=boxColor)
        # place content in box
        for iLine, line in enumerate(content[:self._cellH-2]):
            message = line["msg"]
            category = line["category"] if "category" in line.keys() else None
            if inFocus and iLine==eventIndex:
                color = self._optionFocusColor
            elif inFocus:
                color = self._optionContentSelectColor
                # check if has color for work
            else:
                color = setup["colors"][category] if category in setup["colors"].keys() else self._optionRegularColor
            # if text needs to be cut off
            while len(message)<self._cellL-1:
                message+=" "
            if len(message)>self._cellL-1:
                message = message[:self._cellL-2]
                self._text(locsY[rowNumber]+2+iLine,locsX[colNumber]+1,message,color=color)
                self._point(locsY[rowNumber]+2+iLine,locsX[colNumber]+self._cellL-1,curses.ACS_DIAMOND,color=color)
            # show full text
            else:
                self._text(locsY[rowNumber]+2+iLine,locsX[colNumber]+1,message,color=color)

        # message for truncated lines
        if len(content)>self._cellH-2:
            # clear line
            self._text(locsY[rowNumber+1]-1,locsX[colNumber]+1," "*(self._cellL-1),color=boxColor)
            # make new line
            message = "{0} more...".format(len(content)-self._cellH+2)
            if len(message)<self._cellL-3:
                self._text(locsY[rowNumber+1]-1,locsX[colNumber]+4,message,color=boxColor)
            else:
                self._point(locsY[rowNumber+1]-1,locsX[colNumber]+4,curses.ACS_DIAMOND,color=boxColor)

    def _adjustFocus(self,weekShift,dayShift,indexShift):
        """ Attempt to move focus, return False if no problem
            Return True if calendar needs to be re-loaded
        """
        newFocus = dict(self._focus)
        oldFocus = dict(self._focus)

        weekIndex = self._weekNumbers.index(oldFocus["week"])
        dayIndex = newFocus["day"]

        # check if cal needs to be reloaded
        if dayIndex+dayShift<0:
            dayIndex=self._nX-1
            dayShift=0
            weekShift-=1
        elif dayIndex+dayShift>=self._nX:
            dayIndex=0
            dayShift=0
            weekShift+=1

        # check if cal needs to be reloaded
        if weekIndex+weekShift<0 or weekIndex+weekShift>=len(self._weekNumbers):
            return True


        newFocus["week"] = self._weekNumbers[weekIndex+weekShift]
        newFocus["day"]  = dayIndex+dayShift
        content = self._getDateContent(newFocus["week"],newFocus["day"])["content"]
        newFocus["index"] = (newFocus["index"]+indexShift)%max(1,len(content))

        # if newFocus is different, redraw both oldFocus and newFocus
        self._focus = copy.deepcopy(newFocus)
        if newFocus["week"]!=oldFocus["week"] or newFocus["day"]!=oldFocus["day"]:
            self._drawDayContent(oldFocus["week"],oldFocus["day"])
        self._drawDayContent(newFocus["week"],newFocus["day"])


        return False 

    def _drawDiagnostics(self):
        day = self._backend.today()
        self._text(0,0,str(day))


    ################################################################################
    # Interface
    ################################################################################

    def moveFocus(self,dayDirection=None,indexShift=0):
        """ Move focus up/down, right/left 
            Retrun true if needs to re-fresh
        """
        weekShift = 0
        dayShift = 0
        if dayDirection==0:
            weekShift=-1
        if dayDirection==1:
            dayShift = 1
        if dayDirection==2:
            weekShift=1
        if dayDirection==3:
            dayShift = -1
        return self._adjustFocus(weekShift,dayShift,indexShift)

    def _loadDayContent(self,date):
        """ Main interface function for placing text in calendar view
            content is a list of strings, line by line
            week matches a week number in _weekNumbers 
        """
        dayNumber = date.weekday()
        weekNumber = date.isocalendar()[1]
        backend = self._backend
        # check inputs
        if weekNumber not in self._weekNumbers:
            raise BaseException("Week {0} not in _weekNumbers {1}".format(week,self._weekNumbers))
        if dayNumber<0 or dayNumber>self._nX:
            raise BaseException("Day {0} out of range".format(day))
        # add content to memory
        if weekNumber not in self._content.keys(): self._content[weekNumber]={}
        if dayNumber not in self._content[weekNumber].keys(): self._content[weekNumber][dayNumber]=[]
        content = backend.getDay(date)
        self._content[weekNumber][dayNumber]={"content":content,"date":date}
        # self._drawDayContent(week,day)

    def updateDay(self,date):
        """ Update a day based on a date object """
        day = date.weekday()
        week = date.isocalendar()[1]
        self._loadDayContent(date)
        self._drawDayContent(week=week,day=day)
