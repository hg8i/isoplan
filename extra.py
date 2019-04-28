def firstUpper(s):
    return s[0].upper()+s[1:]

def yellow(*string):
    """ return string as red """
    string = [str(s) for s in string]
    ret = "\033[33m{0}\033[39m".format(" ".join(string))
    return ret

def red(*string):
    """ return string as red """
    string = [str(s) for s in string]
    ret = "\033[31m{0}\033[39m".format(" ".join(string))
    return ret

def green(*string):
    """ return string as green """
    string = [str(s) for s in string]
    ret = "\033[32m{0}\033[39m".format(" ".join(string))
    return ret

