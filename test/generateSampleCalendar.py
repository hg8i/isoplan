

import datetime, time, calendar
from extra import *
now = datetime.datetime.now()
import random, string
import cPickle as pickle
import time, os


i=0
os.popen("mkdir example")
for year in [2018,2019]:
    yearDict = {}
    for month in range(1,13):
        for day in range(1,calendar.monthrange(year,month)[1]+1):
            d = datetime.date(year, month, day)
            print year, month, day, d
            for j in range(random.randint(0,2)):
            # for j in range(13):
                if d not in yearDict.keys(): yearDict[d] = []
                msg = "{0} on this day {1}".format("".join([string.ascii_letters[k] for k in range(random.randint(5,10))]),j)
                uniqueId = time.time()*10+i
                i+=1
                category = ["work","home"][random.randint(0,1)]
                yearDict[d].append({"id":uniqueId,"msg":msg,"category":category})
    path = "example/{0}.pickle".format(year)
    pickle.dump(yearDict,open(path,"w"))


