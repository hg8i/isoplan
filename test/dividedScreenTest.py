from __future__ import division
import math, sys, time, copy
import curses
import logging
import numpy as np
import datetime
import curses, sys, os, time
from curses import wrapper
from calendarView import *
from textView import *
from backend import *

def _text(window,y,x,s,color=20):
    window.move(int(y),int(x))
    window.addstr(str(s),curses.color_pair(color))


def main(screen):
    curses.init_pair(20, 0, 15)
    y,x = screen.getmaxyx()
    frac = 0.75
    screen1 = screen.subwin(int(y*frac)-1,x,0,0)
    screen2 = screen.subwin(int(y*(1-frac))-1,x,int(y*frac),0)


    _text(screen1,1,1,"screen1")
    _text(screen2,1,1,"screen2")
    screen1.border()
    screen2.border()
    screen1.refresh()
    screen2.refresh()

    count=0

    while True:
        # c = screen.getch()
        c = screen1.getch()
        count+=1

        if c == curses.KEY_RESIZE:
            screen1.clear()
            screen.clear()
            screen2.clear()
            y,x = screen.getmaxyx()

            # screen1 = screen.subwin(int(y*frac)-1,x,0,0)
            # screen2 = screen.subwin(int(y*(1-frac))-1,x,int(y*frac),0)

            # screen1.mvwin(0,0)
            # screen2.mvwin(int(y*(1-frac)),0)

            # screen1.resize(int(y*frac)-1,x)
            # screen2.resize(int(y*(1-frac))-1,x)

        _text(screen1,1,1,"screen1: {0}".format(count))
        _text(screen2,1,1,"screen2: {0}".format(count))
        screen1.border()
        screen2.border()
        screen1.refresh()
        screen2.refresh()
        screen.refresh()






wrapper(main)

