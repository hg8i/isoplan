from __future__ import division
import math, sys, copy
import curses
import logging
import numpy as np
import datetime

# from drawingFunctions import *
from drawingFunctions import _drawBox, _drawBoxOutline, _print, _text, _point

"""
Text box view of events in that day
"""

class textView:
    def __init__(self,window,setup,backend):

        # margins, should depend on calendar view
        self._leftMargin   = 4
        self._rightMargin  = 4
        self._topMargin    = 0
        self._bottomMargin = 1
        self._setup = setup

        self._window = window
        self._optionRegularColor   = setup["colors"]["default"]
        self._optionHighlightColor = setup["highlights"]["default"]
        self._optionFocusColor     = setup["colors"]["focus"]

        self._backend = backend
        if window!=None:
            self.update(window)

    def _drawBorder(self):
        # draw box border
        height = self._screenY-self._topMargin-self._bottomMargin
        width = self._screenX-self._rightMargin-self._leftMargin
        x = self._leftMargin
        y = self._topMargin
        _drawBox(self._window,y,x,height,width," ",self._optionRegularColor)
        _drawBoxOutline(self._window,y,x,height,width,"X",self._optionRegularColor)

    def _writeDayInfo(self):
        day = self._backend.today()
        content = self._backend.getDay(day)
        eventIndex = self._backend.getEventIndex()
        contentHeight = self._height-2
        setup = self._setup

        # header
        _text(self._window,self._topMargin,self._leftMargin+1,day, color=self._optionHighlightColor)
        # _text(self._window,self._topMargin,self._width+self._leftMargin-2,eventIndex,color=self._optionHighlightColor)

        # scrolling down when event is out of range
        shift = 0
        # shift = eventIndex-contentHeight
        while eventIndex!=None and eventIndex-shift>contentHeight:
            shift+=1

        x = self._leftMargin+1
        for y,data in enumerate(content):
            thisLine = content[y+shift]
            message = thisLine["msg"]
            category  = thisLine["category"] if "category" in thisLine.keys() else ""
            eventTime = thisLine["time"]     if "time" in thisLine.keys() else ""
            notes     = thisLine["notes"]    if "notes" in thisLine.keys() else ""
            truncated=False
            if eventTime!="":
                message="{0}: {1}".format(eventTime,message)
            else: message=">> {0}".format(message)
            if notes!="":
                message+=" -> {0}".format(notes)
            if len(message)>self._width-4:
                message=message[:self._width-6]
                truncated=True
            # focused
            if y+shift==eventIndex:
                # can change focus color, but choose not to
                color = self._optionRegularColor
                _point(self._window,self._topMargin+y+1,self._leftMargin+2,curses.ACS_DIAMOND,color=self._optionRegularColor)

            else: # regular
                color = setup["colors"][category] if category in setup["colors"].keys() else self._optionRegularColor
            _text(self._window,self._topMargin+y+1,self._leftMargin+4,message,color=color)
            # diamond indicate truncated info
            if truncated:
                _point(self._window,self._topMargin+y+1,self._leftMargin+self._width-1,curses.ACS_DIAMOND,color=color)
            # draw cutoff message if too many events
            if y>=contentHeight and y<len(content)-1: 
                nUnseen = len(content)-contentHeight-1
                cutoff = "... {0} unseen event{1} ...".format(nUnseen,["","s"][nUnseen>1])
                _text(self._window,contentHeight+2,self._leftMargin+int((self._width-len(cutoff))/2),cutoff,color=self._optionHighlightColor)
                break

    def update(self,window):
        """ Update text view """
        self._window = window
        # self._window.clear()
        self._screenY,self._screenX = self._window.getmaxyx()
        self._width  = self._screenX-self._leftMargin-self._rightMargin
        self._height = self._screenY-self._topMargin-self._bottomMargin
        # _print("textscreen",self._window.getmaxyx())
        if self._screenY<=2: return
        # self._window.clear()
        self._drawBorder()
        self._writeDayInfo()
        # _print(self._backend.today())
        self._window.refresh()
        # _print("Success drawing textView")
