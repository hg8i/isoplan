
"""
# Interface for drawing the calendar in curses
"""

from backend import *

def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()






class interface:
    def __init__(self,screen):
        """ Interface handels creating 
            1) Calendar view
            2) Text details view
            3) Text input window
        """
        self._screen = screen
        curses.curs_set(0)
        # screen.clear()
        os.popen("rm log.txt")

        self._calFrac = 0.75
        self._nWeeks = 2

        # loads colors
        self._loadSettings()

        # make sub-windows
        screenY,screenX = screen.getmaxyx()
        calY = int(screenY*self._calFrac)
        self._calScr = screen.subwin(calY,screenX,0,0)
        textY = int(screenY*(1-self._calFrac))
        self._textScr = screen.subwin(textY-1,screenX,calY+1,0)

        self._backend = backend(self._settings)
        # b.prevMonth()
        # b.prevMonth()
        # b.prevMonth()
        self._cal = self._makeCal(self._calScr,self._nWeeks,self._nWeeks)

        self._text = textView(self._textScr,self._settings,self._backend)

        # screen.refresh()

        self._eventBuffer = None

        self.run()


    def _makeCal(self,screen,weekLow,weekHigh):
        backend = self._backend
        setup = {}
        setup["weekData"] = []
        setup["focus"] = {"week":backend._today.isocalendar()[1],"day":backend._today.weekday(),"index":0}
        setup["weekLow"]  = weekLow
        setup["weekHigh"] = weekHigh
        # copy in global settings
        # screen.clear()
        setup.update(self._settings)

        cal = calendarView(screen,setup,backend)
        return cal


    def _loadSettings(self):
        self._settings = {}
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        # parse category colors (work cal, home cal, etc)
        colors = {}
        highlights = {}
        shift = 230
        for i, category in enumerate(settings.userColors.keys()):
            colorPair = list(settings.userColors[category])
            curses.init_pair(shift+i*2,  colorPair[0],colorPair[1])
            curses.init_pair(shift+i*2+1,colorPair[1],colorPair[0])
            colors[category] = shift+i*2
            highlights[category] = shift+i*2+1
        ### Diagnostic
        # for i in range(0, 255):
        #     self._screen.addstr(str(i-1)+" ", curses.color_pair(i))
        # self._screen.getch()
        self._settings["colors"] = colors
        self._settings["highlights"] = highlights

        # calendar data path
        self._settings["calPath"] = settings.calPath
        # default category
        self._settings["mainCategory"] = settings.mainCategory

        # load month, day names
        self._settings["dayNames"] = settings.dayNames
        self._settings["monthNames"] = settings.monthNames

    def _getNewEvent(self,day):
        """ Make new event from scratch """
        # make empty event
        uniqueId = time.time()
        msg = ""
        category = self._settings["mainCategory"]
        event = {"id":uniqueId,"msg":msg,"category":category}
        return self._changeEvent(day,event)

    def _changeEvent(self,day,event):
        """ Make new event from scratch """
        # make empty event
        # make screen
        screen = self._screen
        screenY,screenX = screen.getmaxyx()
        height = min(screenY,20) - 1
        width = min(screenX,80) - 1
        x = int((screenX-width)/2)
        y = int((screenY-height)/2)
        dialogScreen = screen.subwin(height,width,y,x)
        edits = editDialog(dialogScreen,self._settings,day,event)
        return edits.run()

    def _makeScreens(self):
        """ Make screen for text details object """
        screenY,screenX = self._screen.getmaxyx()
        calY = int(screenY*self._calFrac)
        calScr = self._screen.subwin(calY,screenX,0,0)
        textY = int(screenY*(1-self._calFrac))
        textScr = self._screen.subwin(textY-1,screenX,calY+1,0)
        return calScr,textScr

    def run(self):
        """ Run loop for main program """
        nWeeks = self._nWeeks
        calScr = self._calScr
        textScr = self._textScr
        backend = self._backend
        screen = self._screen

        while True:
            # Store the key value in the variable `c`
            # c = screen.getch()
            c = calScr.getch()

            # Clear the terminal
            # screen.clear()
            if c == ord("a"):
                pass

            # up/down one day
            elif c == ord("h"):
                backend.prevDay()
                if self._cal.moveFocus(dayDirection=3):
                    self._cal = self._makeCal(calScr,0,nWeeks*2)
            elif c == ord("l"):
                backend.nextDay()
                if self._cal.moveFocus(dayDirection=1):
                    self._cal = self._makeCal(calScr,nWeeks*2-1,1)

            # down/up one week
            elif c == ord("j"):
                backend.nextWeek()
                if self._cal.moveFocus(dayDirection=2): 
                    self._cal = self._makeCal(calScr,nWeeks*2,0)
            elif c == ord("k"):
                backend.prevWeek()
                if self._cal.moveFocus(dayDirection=0):
                    self._cal = self._makeCal(calScr,0,nWeeks*2)

            # zoom in/out
            elif c == ord("+"):
                nWeeks+=1
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)
            elif c == ord("-"):
                nWeeks = max(1,nWeeks-1)
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)
            elif c == ord("="):
                nWeeks = 2
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)

            # center calendar on selected day
            elif c == ord("g"):
                backend.goNow()
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)

            # jump to top/bottom
            elif c == ord("H"):
                while not self._cal.moveFocus(dayDirection=0):
                    backend.prevWeek()
                self._cal.update()
            elif c == ord("L"):
                while not self._cal.moveFocus(dayDirection=2):
                    backend.nextWeek()
                self._cal.update()


            # up/down one month
            elif c == ord("N"):
                backend.prevEvent()
                self._cal.update()
            elif c == ord("n"):
                backend.nextEvent()
                self._cal.update()

            # create new event
            elif c == ord("i"):
                day = backend.today()
                changed,event = self._getNewEvent(day)
                if changed:
                    backend.addEvent(day,event)
                    self._cal.updateDay(day)
                self._cal.update()

            # edit existing event, or create new one if empty
            elif c in [ord("c"),10]:
                day = backend.today()
                content = backend.getDay(day)
                eventIndex = backend.getEventIndex()
                if eventIndex==None: 
                    changed,event = self._getNewEvent(day)
                else:
                    changed,event = self._changeEvent(day,content[eventIndex])
                if changed and len(event["msg"].replace(" ",""))>0:
                    backend.deleteEvent(day,event["id"])
                    backend.addEvent(day,event)
                self._cal.update()

            # up/down one month
            elif c == ord("u"):
                backend.prevMonth()
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)
                self._cal.update()
            elif c == ord("d"):
                backend.nextMonth()
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)
                self._cal.update()

            # yank event
            elif c == ord("y"):
                day = backend.today()
                content = backend.getDay(day)
                eventIndex = backend.getEventIndex()
                if eventIndex==None: continue
                self._eventBuffer = dict(content[eventIndex])
            # yank event
            elif c == ord("p"):
                day = backend.today()
                if self._eventBuffer==None: continue
                backend.addEvent(day,self._eventBuffer)
                self._cal.updateDay(day)
                self._cal.update()


            # delete event
            elif c == ord("x"):
                day = backend.today()
                content = backend.getDay(day)
                eventIndex = backend.getEventIndex()
                if eventIndex==None: continue
                self._eventBuffer = dict(content[eventIndex])
                backend.deleteEvent(day,content[eventIndex]["id"])
                self._cal.updateDay(day)
                self._cal.update()


            elif c == curses.KEY_RESIZE:
                calScr.clear()
                textScr.clear()
                screen.clear()
                calScr, textScr = self._makeScreens()
                screen.refresh()
                self._text.update(textScr)
                self._cal.update(calScr)
            elif c == ord("q"):
                return
            elif c == curses.KEY_UP:
                calScr.addstr("")
            else:
                calScr.addstr("")

            # diagnostics
            self._text.update(textScr)


def main(screen):
    i = interface(screen)

import curses, sys, os, time
import curses.textpad as textpad
from curses import wrapper
from calendarView import *
from textView import *
from backend import *
from editDialog import *
import settings

wrapper(main)

