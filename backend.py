import cPickle as pickle
import datetime, time, calendar
import sys, os, copy
from extra import *
from datetime import timedelta

"""
# Class for holding data related to a year
"""
class year:
    def __init__(self,year,setup):
        self._year = year
        self._calPath = setup["calPath"]
        dirPath = os.path.dirname(os.path.realpath(__file__))
        # make directory is not existing
        os.popen("mkdir -p {0}/{1}".format(dirPath,self._calPath))
        self._path = "{0}/{1}/{2}.pickle".format(dirPath,self._calPath,self._year)
        self._data = None
        self._fileModifiedTimeOnLoad = None 
        self._load()

    def _load(self):
        """ Load data for this year """
        # check if file exists, otherwise make new
        if os.path.isfile(self._path):
            self._data = pickle.load(open(self._path))
        else:
            # print "DEBUG:: creating new year file"
            self._data = {}
            self._update()

        # get date of last file modification
        self._fileModifiedTimeOnLoad = os.path.getmtime(self._path)

    def resolveFileConflicts(self):
        """ If file has been modified since it was loaded, resolve conflicts
            Return 1 if conflict resolved, 0 otherwise
        """ 
        # get date of last modification in case a conflict needs to be resolved
        fileModifiedTime = os.path.getmtime(self._path)
        if fileModifiedTime!=self._fileModifiedTimeOnLoad:
            # save current data 
            oldData = copy.copy(self._data)
            # load more recent data
            self._load()
            print len(oldData), len(self._data)
            # quit()
            return 1
        return 0

    def _update(self):
        """ Update the saved database after a change """
        f = open(self._path,"w")
        pickle.dump(self._data,f)
        # update file modified
        self._fileModifiedTimeOnLoad = os.path.getmtime(self._path)
        f.close()

    def addEvent(self,day,newEvent):
        """ Add event to dataset 
            Event is a dict with at least "id", "msg", "category" as keys
            Day is a datetime.date
        """
        # print "DEBUG:: adding event"
        if len(newEvent["msg"].replace(" ",""))==0: return
        if day not in self._data.keys():
            self._data[day]=[]
        # only add event if uniqueId doesn't already exist
        uniqueIds = [d["id"] for d in self._data[day] if "id" in d.keys()]
        if newEvent["id"] not in uniqueIds:
            self._data[day].append(newEvent)
        # self._data[day].append(newEvent)
        # sort by time
        f = lambda x: x["time"] if "time" in x.keys() else 0
        self._data[day]=sorted(self._data[day],key=f)
        # update saved database after making a change
        self._update()

    def deleteEvent(self,day,uniqueId):
        """ Delete an event from the dataset based on the day, ID
        """
        for iEvent,event in enumerate(self._data[day]):
            if event["id"]==uniqueId:
                self._data[day].pop(iEvent)
                break
        # update saved database after making a change
        self._update()

    def getDay(self,day):
        """ Return dicts corresponding to day 
        """
        if day not in self._data.keys():
            self._data[day]=[]
        # sort by time
        f = lambda x: x["time"] if "time" in x.keys() else 0
        self._data[day]=sorted(self._data[day],key=f)
        return self._data[day]
    

    def __str__(self):
        nEvents = sum([len(x) for x in self._data.values()])
        nDays   = len(self._data.keys())
        # print self._data
        return "[Year container for {0}, {1} days, {2} events]".format(self._year,nDays,nEvents)




"""
# Server backend for managing:
    * Adding/deleting calendar events
    * Loading calendar events
"""
class backend:
    def __init__(self,setup):
        self._setup = setup
        # self._eventIndex = 0 # which event in the day is in focus
        self.goNow()
        self._years = {}

    def resolveFileConflicts(self):
        """ If a loaded year file has been modified since it was loaded, resolve conflicts
            Return 1 if conflict resolved, 0 otherwise
        """ 
        conflictFound = False
        for year in self._years.keys():
            conflictFound = conflictFound or self._years[year].resolveFileConflicts()
        return conflictFound

    def _loadDay(self,day):
        """ Loads current year into dict _years """
        thisYear = day.year
        if thisYear not in self._years.keys():
            self._years[thisYear] = year(thisYear,self._setup)


    def addEvent(self,day,newEvent):
        """ Add event to dataset 
            Update event index if first event added
            Event is a dict with at least "msg", "category" as keys
            Day is a datetime.date
        """
        self._loadDay(day)
        self._years[self._today.year].addEvent(day,newEvent)
        if self._eventIndex==None:
            self._eventIndex = 0

    def deleteEvent(self,day,uniqueId):
        self._loadDay(day)
        self._years[self._today.year].deleteEvent(day,uniqueId)
        nEvents = len(self.getDay())
        if nEvents == 0:
            self._eventIndex = None
        else:
            self._eventIndex%=nEvents

    def getDay(self,day=None):
        if day==None: day = self._today
        self._loadDay(day)
        day = self._years[day.year].getDay(day)
        return day

    def _daysThisMonth(self,offset=0):
        """ Return number of days this month 
            Offset month by offset 
        """
        monthNumber = self._today.month+offset
        yearNumber = self._today.year
        while monthNumber>12:
            monthNumber-=12
            yearNumber+=1
        while monthNumber<1:
            monthNumber+=12
            yearNumber-=1
        return calendar.monthrange(yearNumber,monthNumber)[1]

    # def getMonth(self):
    #     """ Return the datetimes for current month """
    #     days = []
    #     for iDay in range(self._daysThisMonth()):
    #         day = datetime.date(self._today.year,self._today.month,1+iDay)
    #         days.append(day)
    #     return days

    def _copyToday(self):
        return datetime.date(self._today.year,self._today.month,self._today.day)

    def today(self):
        return self._today

    def toweek(self):
        return self.today().isocalendar()[1]


    def getWeek(self,offset=0):
        """ Return days comprising this week, and weeknumber
            Week is shifted by offset
        """
        offset = int(offset)
        day = self._copyToday()
        # jump by offset
        day += timedelta(weeks=offset)
        # jump to start of week
        day -= timedelta(days=day.weekday())
        # make list of days this week
        days = []
        for iDay in range(7):
            days.append(day)
            day += timedelta(days=1)
        return days

    def getWeekNumber(self,offset=0):
        """ Return the week number and year, with offset in weeks"""
        offset = int(offset)
        day = self._copyToday()+timedelta(weeks=offset)
        week = day.isocalendar()[1]
        year = day.isocalendar()[0]
        month = day.month
        # if week == 53: week = 0 # python convention
        return {"week":week,"year":year,"month":month}

    ###### Event index controls ########
    def getEventIndex(self):
        """ Returns index of event in focus """
        nEvents = len(self.getDay())
        if nEvents==0: return None
        return self._eventIndex
    def prevEvent(self):
        """ Increment previous event index """
        nEvents = len(self.getDay())
        if nEvents==0: return
        self._eventIndex = (self._eventIndex-1)%nEvents
    def nextEvent(self):
        """ Increment next event index """
        nEvents = len(self.getDay())
        if nEvents==0: return
        self._eventIndex = (self._eventIndex+1)%nEvents
    ###### /Event index controls ########

    def nextDay(self):
        """ Move to next day """
        self._eventIndex = 0
        self._today += timedelta(days=1)

    def prevDay(self):
        """ Move to prev day """
        self._eventIndex = 0
        self._today -= timedelta(days=1)

    def nextWeek(self):
        """ Move to next week """
        self._eventIndex = 0
        self._today += timedelta(days=7)

    def prevWeek(self):
        """ Move to prev week """
        self._eventIndex = 0
        self._today -= timedelta(days=7)

    def nextMonth(self):
        """ Move to next month, try to set day to similar day """
        # jump to end of month, plus min(n days in next month, original day)
        self._eventIndex = 0
        originalDay = self._today.day
        jump = (self._daysThisMonth()-originalDay) + min(originalDay,self._daysThisMonth(offset=1))
        self._today += timedelta(days=jump)

    def prevMonth(self):
        """ Move to prev month, try to set day to similar day """
        # jump to start of prev month, plus min(n days in prev month, original day)
        self._eventIndex = 0
        originalDay = self._today.day
        jump = originalDay + self._daysThisMonth(offset=-1) - min(originalDay,self._daysThisMonth(offset=-1))
        self._today += timedelta(days=-jump)

    def goNow(self):
        """ Go to current real day """
        self._eventIndex = 0
        self._today = self.now()

    def now(self):
        """ Return now """
        now = datetime.datetime.now()
        self._now = datetime.date(now.year,now.month,now.day)
        return self._now


    def __str__(self):
        ret = "="*40+"\n"
        ret+= "Today="+str(self._today)+"\n"
        for year in self._years.keys():
            ret += "\t{0}: {1}\n".format(year,self._years[year])
        ret+= "="*40+"\n"
        return ret


if __name__=="__main__":

    now = datetime.datetime.now()
    today = datetime.date(now.year,now.month,now.day)
    tomorrow = today+timedelta(days=0)

    b = backend()
    event = {"id":12334,"msg":"Hello this is event","category":"work"}
    b.addEvent(today,event)
    b.addEvent(tomorrow,event)
    b.removeEvent(today,12334)

    print "Today", today
    for e in b.getDay(today):
        print e
    print "Tomorrow", tomorrow
    for e in b.getDay(tomorrow):
        print e

    print "="*40
    print b
    b.prevMonth()
    b.nextMonth()
    print b

    print "="*40
    print b.getWeek()
    b.nextWeek()
    print b.getWeek()
    print "="*40

