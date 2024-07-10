import urllib
from urllib import request
from collections import OrderedDict
import datetime

def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()


def parseEvent(primitive):
    """ Parse primitive event list-by-line into dictionary
    """
    event={}
    event = OrderedDict()
    for dat in primitive:
        # print dat
        if ":" in dat:
            # Add entry to dictionary
            event[dat.split(":")[0]] = ":".join(dat.split(":")[1:])
        elif len(event.keys())>0:
            # Try adding to previous entry
            event[list(event.keys())[-1]]
    return event

def icsConvertData(icsDate):
    """ Convert ICS date and time, return """
    # 1998 04 15 T23 59 59
    # print "converting",icsDate
    year  = int(icsDate[0:4])
    month = int(icsDate[4:6])
    day   = int(icsDate[6:8])
    date  = datetime.date(year,month,day)
    time=None
    timezone=2
    if "T"  in icsDate: 
        time   = icsDate[9:13]
        minute = int(icsDate[11:13])
        hour   = int(icsDate[9:11])
        # Assume offset (this is hacky, not sure if Z is timezone)
        # This should be replaced - only because times came later
        # hour="1"*(timezone-len(hour))+hour
        # hour=int(hour)+timezone

        time=f"{str(hour).zfill(2)}{str(minute).zfill(2)}"
        time=f"{str(hour+1).zfill(2)}{str(minute).zfill(2)}"

        # _print("DATE:",icsDate,time,hour,minute)


        # if "Z" in icsDate: 
        #     # Increment hour and day according to timezone
        #     hour="1"*(timezone-len(hour))+hour
        #     time=hour+minute
        #     # increment date incase of rollover
        #     # date+=datetime.timedelta(days=1)
        #     # date+=datetime.timedelta(hours=2)

    # quit()
    # if "Z" in icsDate: date+=datetime.timedelta(hours=1)
    return date,time

def downloadIcs(url):
    """ Download ICS file via URL
        Return as list of "event dictionaries" 
    """
    response = request.urlopen(url).read().splitlines()
    response = [s.decode("utf-8") for s in response]
    # _print("="*50)
    # _print(response)
    # _print("="*50)
    # checks
    if response[0]!="BEGIN:VCALENDAR": raise BaseException("Bad ICS response")
    if response[-1]!="END:VCALENDAR": raise BaseException("Bad ICS response")
    events = []
    event=[]
    for line in response:
        if "BEGIN:VEVENT" in line:
            event=[]
        elif "END:VEVENT" in line:
            events.append(parseEvent(event))
        else: event.append(line)
    return events

def getEventsWithUrl(url,args=[]):
    """ Download ICS file, convert for isocal, return events 
    """
    # add arguements if given
    if args and url[-1]!="?":url+="?"
    url+="&".join(args)

    events = downloadIcs(url)
    for iEvent, event in enumerate(events):
        for key in event.keys():
            if "DT" in key:
                date,time = icsConvertData(event[key])
                events[iEvent][key]={"date":date,"time":time}
                # print key, date,time
        # this is the map between ICS and isocal
        _print( event.keys())
        # events[iEvent]["day"]     = event["DTSTART;VALUE=DATE-TIME"]["date"]
        # events[iEvent]["time"]    = event["DTSTART;VALUE=DATE-TIME"]["time"]
        events[iEvent]["day"]     = event["DTSTART"]["date"]
        events[iEvent]["time"]    = event["DTSTART"]["time"]
        events[iEvent]["uniqueId"]= event["UID"]
        events[iEvent]["msg"]     = event["SUMMARY"]
        events[iEvent]["notes"]   = event["URL"]

    return events


if __name__=="__main__":

    import settings
    downloadIcsCalendars = settings.downloadIcsCalendars

    for icsInfo in downloadIcsCalendars:
        icsEvents=getEventsWithUrl(icsInfo["url"],args=icsInfo["args"])
        for event in icsEvents:
            print(event["msg"], event["time"], event["notes"])


    # url= "https://indico.cern.ch/export/categ/5273.ics?from=-31d"
    # events = getEventsWithUrl(url)

    # for e in events:
    #     print e
