from __future__ import division
import math, sys, time, copy
import curses
import logging
import numpy as np
import datetime


def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()

def _move(window,y,x):
    try:
        window.move(int(y),int(x))
    except:
        raise BaseException("Failed moving x={0}, y={1}".format(x,y))


def _hline(window,y,x,l,char=None,color=0):
    if char==None: char = curses.ACS_HLINE
    _move(window,int(y),int(x))
    try:
        window.hline(char,int(l),curses.color_pair(color))
    except:
        _print("Failed while drawing")

def _vline(window,y,x,l,color=0):
    _move(window,int(y),int(x))
    try:
        window.vline(curses.ACS_VLINE,int(l),curses.color_pair(color))
    except:
        _print("Failed while drawing")

def _point(window,y,x,c,color=0):
    _move(window,int(y),int(x))
    try:
        window.addch(c,curses.color_pair(color))
    except:
        _print("Failed while drawing")

def _text(window,y,x,s,color=20):
    _move(window,int(y),int(x))
    try:
        label=str(s)
        window.addstr(label,curses.color_pair(color))
    except:
        label=repr(s)
        window.addstr(label,curses.color_pair(color))

def _drawBox(window,y,x,h,l,char,color):
    """ Draw rectangle filled with shaded character """
    # for yPos in range(int(y),int(y+h)):
    for line in range(h):
        _hline(window,y+line,x,l,char,color=color)

def _drawBoxOutline(window,y,x,h,l,char,color):
    """ Draw rectangle """
    _hline(window,y,x,l)
    _hline(window,y+h,x,l)
    _vline(window,y,x,h)
    _vline(window,y,x+l,h)

    _point(window,y,x,curses.ACS_ULCORNER)
    _point(window,y,x+l,curses.ACS_URCORNER)
    _point(window,y+h,x,curses.ACS_LLCORNER)
    _point(window,y+h,x+l,curses.ACS_LRCORNER)


def _clear(window,color):
    """ clear window """
    h,l = window.getmaxyx()
    _drawBox(window,0,0,h,l,"x",color)
    # window.refresh()


