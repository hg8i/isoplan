import datetime


def _print(*string):
    string = [str(s) for s in string]
    string = " ".join(string)
    f = open("log.txt","a")
    f.write(string+"\n")
    f.close()


def isnumeric(s):
    return all([i in "0123456789" for i in s])

def stringToDate(dateString,today):
    """ Convert string into date
        Accepted formats
        DDMMYY
        DDMM
        Month Day Year
        Month Day
        YYYY-MM-DD
    """
    if type(dateString)==datetime.date: return dateString
    if type(dateString)==bool: return None
    if dateString=="": return None
    _print(repr(dateString))
    if isnumeric(dateString) and len(dateString)==6:
        day  =int(dateString[0:2])
        month=int(dateString[2:4])
        year =int(dateString[4:6])+2000
    elif isnumeric(dateString) and len(dateString)==4:
        day  =int(dateString[0:2])
        month=int(dateString[2:4])
        year =today.year
    elif len(dateString.split())==3:
        day  =dateString.split()[0]
        month=int(dateString.split()[1])
        year =int(dateString.split()[2])
    elif len(dateString.split())==2:
        day  =dateString.split()[0]
        month=dateString.split()[1]
        year =today.year
    elif len(dateString.split("-"))==3:
        day  =int(dateString.split("-")[2])
        month=int(dateString.split("-")[1])
        year =int(dateString.split("-")[0])
    else: return None

    until = datetime.date(year,month,day)

    return until

