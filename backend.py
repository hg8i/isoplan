import pickle
import datetime, time, calendar
import sys, os, copy
from extra import *
from datetime import timedelta

def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()


"""
# Class for holding data related to a year
"""
class year:
    def __init__(self,year,setup):
        self._year = year
        self._calPath = setup["calPath"]
        # dirPath = os.path.dirname(os.path.realpath(__file__))
        # make directory is not existing
        os.popen("mkdir -p {0}".format(self._calPath))
        self._path = "{0}/{1}.pickle".format(self._calPath,self._year)
        self._singleEventData = None
        self._fileModifiedTimeOnLoad = None 
        self._load()

    def _load(self):
        """ Load data for this year """
        # check if file exists, otherwise make new
        if os.path.isfile(self._path):
            _print("Loading pickle:",self._path)
            self._singleEventData = pickle.load(open(self._path,"rb"))
        else:
            _print("No file to load",self._path)
            # print "DEBUG:: creating new year file"
            self._singleEventData = {}
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
            oldData = copy.copy(self._singleEventData)
            # load more recent data
            self._load()
            print(len(oldData), len(self._singleEventData))
            # quit()
            return 1
        return 0

    def _update(self):
        """ Update the saved database after a change """
        f = open(self._path,"wb")
        pickle.dump(self._singleEventData,f)
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
        if day not in self._singleEventData.keys():
            self._singleEventData[day]=[]
        # only add event if uniqueId doesn't already exist
        uniqueIds = [d["id"] for d in self._singleEventData[day] if "id" in d.keys()]
        if newEvent["id"] not in uniqueIds:
            self._singleEventData[day].append(newEvent)
        # self._singleEventData[day].append(newEvent)
        # sort by time
        f = lambda x: x["time"] if "time" in x.keys() else 0
        self._singleEventData[day]=sorted(self._singleEventData[day],key=f)
        # update saved database after making a change
        self._update()

    def deleteEvent(self,day,uniqueId):
        """ Delete an event from the dataset based on the day, ID
        """
        for iEvent,event in enumerate(self._singleEventData[day]):
            if event["id"]==uniqueId:
                self._singleEventData[day].pop(iEvent)
                break
        # update saved database after making a change
        self._update()

    def getDay(self,day):
        """ Return dicts corresponding to day 
        """
        if day not in self._singleEventData.keys():
            self._singleEventData[day]=[]
        # sort by time
        f = lambda x: x["time"] if "time" in x.keys() else 0
        self._singleEventData[day]=sorted(self._singleEventData[day],key=f)
        return self._singleEventData[day]
    

    def __str__(self):
        nEvents = sum([len(x) for x in self._singleEventData.values()])
        nDays   = len(self._singleEventData.keys())
        # print self._singleEventData
        return "[Year container for {0}, {1} days, {2} events]".format(self._year,nDays,nEvents)


# class eventPattern:
#     def __init__(self):
#         # matching info
#         self._matchingDays = None # list of day-numbers [0-7] to match
#         self._vetoDays     = None # list of days to not match
#         self._matchBefore  = None # latest day to match until
#         self._matchAfter   = None # earliest day to match from
#         # event info
#         self._msg = None
#         self._id = None
#         self._time = None
#         self._notes = None
#         self._category = None


#     def resolve(self,day):
#         """ Return true if this pattern matches this day
#             Day is a datetime.date(now.year,now.month,now.day) object
#         """
#         if day in self._vetoDays:
#             return False
#         if day<self._matchAfter:
#             return False
#         if day>self._matchBefore:
#             return False
#         if day.day in self._matchingDays:
#             return True
#         return False

#     def event(self,day):
#         """ Returns event dictionary for this day
#         """
#         ret = {}
#         ret["msg"] = self._msg
#         ret["id"] = self._id
#         ret["time"] = self._time
#         ret["notes"] = self._notes
#         ret["category"] = self._category
#         # Specific to pattern events
#         ret["patternEvent"] = True
#         ret["masked"] = False
#         return ret


# class repeatingEvents:
#     # Class to store patterns for repeating events, and then populate the year dictionary
#     def __init__(self,inPath="data/repeating.pickle"):
#         self._path = inPath
#         if os.path.isfile(self._path):
#             self._patterns = pickle.load(self._path)
#         else:
#             self._patterns = []

#     def returnEventsForDay(self,day):
#         """ Return events matching particular day
#         """
#         events = [p.event(day) for p in self._patterns if p.resolve(day)]
#         return events




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

    print("Today", today)
    for e in b.getDay(today):
        print(e)
    print("Tomorrow", tomorrow)
    for e in b.getDay(tomorrow):
        print(e)

    print("="*40)
    print(b)
    b.prevMonth()
    b.nextMonth()
    print(b)

    print("="*40)
    print(b.getWeek())
    b.nextWeek()
    print(b.getWeek())
    print("="*40)

