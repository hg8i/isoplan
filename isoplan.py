#!/usr/bin/env python3


"""
# Interface for drawing the calendar in curses
"""

from backend import *
from utils import *
import utils
import random
from multiprocessing import Manager, Process, Semaphore


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

        self._nWeeks = 2

        # loads colors
        self._loadSettings()


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
        shift = 0
        # shift = 230
        # test(settings.userColors.keys())
        utils._print(settings.userColors.keys()); 

        for i, category in enumerate(settings.userColors.keys()):
            i+=100 # not sure about this, must be used elsewhere
            colorPair = list(settings.userColors[category])
            curses.init_pair(shift+i*2,  colorPair[0],colorPair[1])
            curses.init_pair(shift+i*2+1,colorPair[1],colorPair[0])
            colors[category] = shift+i*2
            highlights[category] = shift+i*2+1

        # if 1:
        #     colorPair = list(settings.userColors["work"])
        #     curses.init_pair(shift+i*2,  colorPair[0],colorPair[1])
        #     curses.init_pair(shift+i*2+1,colorPair[1],colorPair[0])
        #     colors["work"] = shift+i*2
        #     highlights["work"] = shift+i*2+1


        ### Diagnostic
        # for i in range(0, 255):
            # self._screen.addstr(str(i-1)+" ", curses.color_pair(i))
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

        # download ICS calendars
        self._settings["downloadIcsCalendars"] = settings.downloadIcsCalendars

        self._showTextbox = settings.showTextbox
        self._textboxFrac = settings.textboxFrac

    # def _rmEventsByPattern(self):
    #     """ Remove events with given color
    #     """
    #     for icsInfo in self._settings["downloadIcsCalendars"]:
    #         icsEvents=icsDownload.getEventsWithUrl(icsInfo["url"],args=icsInfo["args"])
    #         # add events, if not already exist
    #         for icsEvent in icsEvents:
    #             day           = icsEvent["day"]
    #             event         = {}
    #             event["id"]   = icsEvent["uniqueId"]
    #             event["msg"]  = icsEvent["msg"]
    #             event["time"] = icsEvent["time"]
    #             event["notes"] = icsEvent["notes"]
    #             event["category"] = icsInfo["color"]
    #             self._backend.deleteEvent(day,event["id"])

    def _syncIcsCalendars(self):
        """ Download and sync calendar events from ICS
        """
        ps = []
        sema = Semaphore(12)
        manager = Manager()
        output = manager.dict()

        for icsInfo in self._settings["downloadIcsCalendars"]:
            ps.append(Process(target=icsDownload.getEventsWithUrl,args=(sema,icsInfo,output)))
            # icsEvents=icsDownload.getEventsWithUrl(icsInfo["url"],args=icsInfo["args"])

        for p in ps: p.start()
        for p in ps: p.join()

        for url,icsEvents in output.items():
            # add events, if not already exist
            for icsEvent in icsEvents:
                day           = icsEvent["day"]
                event         = {}
                event["id"]   = icsEvent["uniqueId"]
                event["msg"]  = icsEvent["msg"]
                event["time"] = icsEvent["time"]
                event["notes"] = icsEvent["notes"]
                event["category"] = icsInfo["color"]
                event["icsString"] = icsInfo["icsString"]
                self._backend.addEvent(day,event)


    def _getNewEvent(self,day,repeating=False):
        """ Make new event from scratch """
        # make empty event
        uniqueId = time.time()
        msg = ""
        category = self._settings["mainCategory"]
        event = {"id":uniqueId,"msg":msg,"category":category}
        event["time"] = ""
        event["notes"] = ""
        if repeating:
            event["From"] = day
            event["Until"] = ""
            event["Frequency"] = "Weekly"
        # sanitize
        # event["msg"]=str(repr(event["msg"])[1:-1].split(r"\x")[0])
        # event["category"]=str(repr(event["category"])[1:-1].split(r"\x")[0])
        changed,event = self._changeEvent(day,event)
        return changed,event

    def _changeEvent(self,day,event):
        """ Make new event from scratch """
        # make empty event
        # make screen
        screen = self._screen
        screenY,screenX = screen.getmaxyx()
        height = min(screenY,3*len(event.keys())+4-3)
        width = min(screenX,80) - 1
        x = int((screenX-width)/2)
        y = int((screenY-height)/2)
        dialogScreen = screen.subwin(height,width,y,x)
        edits = editDialog(dialogScreen,self._settings,day,event)
        changed,event = edits.run()
        # resolve until into datetime
        if "From" in event.keys():
            event["From"] = stringToDate(event["From"],day)
            # if invalid date, make no change!
            if event["From"] == None: return 0,{}
        if "Until" in event.keys():
            event["Until"] = stringToDate(event["Until"],day)
            # if invalid date, make no change!
            if event["Until"] == None: return 0,{}
        return changed,event

    def _makeScreens(self):
        """ Make screen for text details object """
        screenY,screenX = self._screen.getmaxyx()
        if self._showTextbox:
            calY = int(screenY*(1-self._textboxFrac))
            calScr = self._screen.subwin(calY,screenX,0,0)
            textY = int(screenY*self._textboxFrac)
            textScr = self._screen.subwin(textY-1,screenX,calY+1,0)
        else:
            calY = int(screenY*(1-self._textboxFrac))
            calScr = self._screen.subwin(screenY,screenX,0,0)
            textScr = None
        return calScr,textScr

    def _fillInRepeatingEvents(self,event):
        """ Fill in events from repeating event
        """
        if "From" not in event.keys(): return
        day = event["From"]
        until = event["Until"]

        # if "until" is BEFORE day, switch until and day
        if until<day:
            day,until=until,day

        # loop over and edd each event
        if event["Frequency"]=="Weekly":
            delta = datetime.timedelta(days=7)

        while day<until:
            event["From"] = day
            self._backend.addEvent(day,event)
            self._cal.updateDay(day)
            day=day+delta

    def run(self):
        """ Run loop for main program """
        nWeeks = self._nWeeks

        # make sub-windows
        calScr, textScr = self._makeScreens()
        self._backend = backend(self._settings)


        self._cal = self._makeCal(calScr,self._nWeeks,self._nWeeks)
        self._text = textView(textScr,self._settings,self._backend)

        b = self._backend
        screen = self._screen

        # quit()

        while True:
            # Store the key value in the variable `c`
            # c = screen.getch()
            c = calScr.getch()

            conflictFound = b.resolveFileConflicts()
            if conflictFound or c==ord("e"):

                # # refresh calendarview with new thing
                # self._screen.clear()
                # # self._cal = self._makeCal(calScr,nWeeks,nWeeks)
                # self._cal.updateDays()
                # self._cal.update()
                # self._screen.refresh()

                # get current week low, high
                weekLow,weekHigh = self._cal.getWeekLowHigh()
                self._cal = self._makeCal(calScr,weekLow,weekHigh)

            # Clear the terminal
            # screen.clear()
            if c == ord("a"):
                pass

            # up/down one day
            elif c == ord("h"):
                b.prevDay()
                if self._cal.moveFocus(dayDirection=3):
                    self._cal = self._makeCal(calScr,0,nWeeks*2)
            elif c == ord("l"):
                b.nextDay()
                if self._cal.moveFocus(dayDirection=1):
                    self._cal = self._makeCal(calScr,nWeeks*2-1,1)

            # down/up one week
            elif c == ord("j"):
                b.nextWeek()
                if self._cal.moveFocus(dayDirection=2): 
                    self._cal = self._makeCal(calScr,nWeeks*2,0)
            elif c == ord("k"):
                b.prevWeek()
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
                b.goNow()
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)

            # jump to top/bottom
            elif c == ord("H"):
                while not self._cal.moveFocus(dayDirection=0):
                    b.prevWeek()
                self._cal.update()
            elif c == ord("L"):
                while not self._cal.moveFocus(dayDirection=2):
                    b.nextWeek()
                self._cal.update()


            # up/down one month
            elif c == ord("N"):
                b.prevEvent()
                self._cal.update()
            elif c == ord("n"):
                b.nextEvent()
                self._cal.update()

            # create new event
            elif c == ord("i"):
                day = b.today()
                changed,event = self._getNewEvent(day,repeating=False)
                if changed:
                    b.addEvent(day,event)
                    self._cal.updateDay(day)
                self._screen.clear()
                self._cal.update()
                self._screen.refresh()
                # screen.refresh()

            # create new repeating event
            elif c == ord("r"):
                day = b.today()
                changed,event = self._getNewEvent(day,repeating=True)
                if changed:
                    self._fillInRepeatingEvents(event)
                # refresh
                self._screen.clear()
                self._cal.update()
                self._screen.refresh()


            # edit existing event, or create new one if empty
            elif c in [ord("c"),10]:
                day = b.today()
                content = b.getDay(day)
                eventIndex = b.getEventIndex()
                if eventIndex==None: 
                    changed,event = self._getNewEvent(day)
                else:
                    changed,event = self._changeEvent(day,content[eventIndex])
                if changed and len(event["msg"].replace(" ",""))>0:
                    b.deleteEvent(day,event["id"])
                    b.addEvent(day,event)
                if changed:
                    self._fillInRepeatingEvents(event)
                self._cal.updateDay(day)
                self._cal.update()

            # # rm events by pattern
            # elif c == ord("e"):
            #     self._rmEventsByPattern() 
            #     self._screen.clear()
            #     self._cal.update()
            #     self._screen.refresh()
            #     # screen.refresh()

            # sync from ICS
            elif c == ord("w"):
                self._syncIcsCalendars() 
                self._screen.clear()
                self._cal.update()
                self._screen.refresh()
                # screen.refresh()

            # up/down one month
            elif c == ord("u"):
                b.prevMonth()
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)
                self._cal.update()
            elif c == ord("d"):
                b.nextMonth()
                self._cal = self._makeCal(calScr,nWeeks,nWeeks)
                self._cal.update()

            # yank event
            elif c == ord("y"):
                day = b.today()
                content = b.getDay(day)
                eventIndex = b.getEventIndex()
                if eventIndex==None: continue
                self._eventBuffer = dict(content[eventIndex])
            # paste event
            elif c == ord("p"):
                day = b.today()
                if self._eventBuffer==None: continue
                # get new random id
                self._eventBuffer["id"] = time.time()
                b.addEvent(day,self._eventBuffer)
                self._eventBuffer = dict(self._eventBuffer) # keep new copy in buffer
                self._cal.updateDay(day)
                self._cal.update()


            # delete event
            elif c == ord("x"):
                day = b.today()
                content = b.getDay(day)
                eventIndex = b.getEventIndex()
                if eventIndex==None: continue
                self._eventBuffer = dict(content[eventIndex])
                b.deleteEvent(day,content[eventIndex]["id"])
                self._cal.updateDay(day)
                self._cal.update()


            elif c == curses.KEY_RESIZE:
                calScr.clear()
                if textScr!=None: textScr.clear()
                screen.clear()
                calScr, textScr = self._makeScreens()
                screen.refresh()
                self._cal.update(calScr)

            elif c == ord("t"):
                calScr.clear()
                if textScr!=None:
                    textScr.clear()
                screen.refresh()
                self._showTextbox = not self._showTextbox
                calScr, textScr = self._makeScreens()
                self._cal.update(calScr)

            elif c == ord("q"):
                return
            elif c == curses.KEY_UP:
                calScr.addstr("")
            else:
                calScr.addstr("")

            # diagnostics
            if self._showTextbox:
                self._text.update(textScr)


os.popen("rm log.txt 2> /dev/null")

def main(screen):
    i = interface(screen)

import curses, sys, os, time
import curses.textpad as textpad
from curses import wrapper
from calendarView import *
from textView import *
from backend import *
from editDialog import *
import icsDownload
import settings
from drawingFunctions import _clear

wrapper(main)

