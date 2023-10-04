import urllib.request
from collections import OrderedDict
import datetime
import settings

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
    # UTC datetime
    utc_dt = datetime.datetime.strptime(icsDate, "%Y%m%dT%H%M%SZ")
    # Convert to current timezone

    _print(settings.timezone)
    _print(datetime.timedelta(settings.timezone))
    timezone = datetime.timezone(datetime.timedelta(hours=settings.timezone))
    local_dt = utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(timezone)

    date = local_dt.date()
    time = local_dt.strftime("%H%M")

    _print(f"Parsed time {icsDate} to {date} and {time}")

    return date,time

# def icsConvertData(icsDate):
#     """ Convert ICS date and time, return """
#     # 1998 04 15 T23 59 59
#     # print "converting",icsDate
#     year  = int(icsDate[0:4])
#     month = int(icsDate[4:6])
#     day   = int(icsDate[6:8])
#     date  = datetime.date(year,month,day)
#     time=None
#     timezone=0
#     if "T"  in icsDate: 
#         time   = icsDate[9:13]
#         minute = icsDate[11:13]
#         hour   = icsDate[9:11]
#         # 2023 09 26 T 120000Z
#         # Assume offset (this is hacky, not sure if Z is timezone)
#         # This should be replaced - only because times came later
#         if "Z" in icsDate: 
#             # Increment hour and day according to timezone
#             hour="1"*(timezone-len(hour))+hour
#             time=hour+minute
#             # increment date incase of rollover
#             # date+=datetime.timedelta(days=1)
#             # date+=datetime.timedelta(hours=2)
#     # if "Z" in icsDate: date+=datetime.timedelta(hours=1)
#     return date,time

def downloadIcs(url):
    """ Download ICS file via URL
        Return as list of "event dictionaries" 
    """
    response = urllib.request.urlopen(url).read().splitlines()
    response = [s.decode("utf-8") for s in response]
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
        for k in event.keys():
            _print("EVENT",k,"::::",event[k])
        # _print( event.keys())
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
            pass
            # print event["msg"], event["time"], event["notes"]


    # url= "https://indico.cern.ch/export/categ/5273.ics?from=-31d"
    # events = getEventsWithUrl(url)

    # for e in events:
    #     print e
