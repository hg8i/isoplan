# Python dictionary for settings

# Dictionary for matching calendar names to a color
# -1 is default
# First number is background, 2nd number is foreground
userColors = {}
userColors["work"]      = [30,-1] # turquoise
userColors["home"]      = [33,-1] # dark blue
userColors["travel"]    = [124,-1] # green
userColors["crit"]      = [214,-1] # orange
userColors["grad"]      = [196,-1] # red
# userColors["default"] = [223,-1]
userColors["default"]   = [-1,-1]
userColors["year"]      = [128,-1]
userColors["month"]     = [220,-1]
userColors["focus"]     = [39,-1]
# userColors["select"]    = [122,0]
userColors["select"]    = [145,0]
userColors["emergency"]   = [9,-1]
userColors["indico"]      = [240,-1]

userColors["dialogFocus"]   = [39,8]
userColors["dialogBackground"]   = [-1,8]

dayNames = ["mon","tues","weds","thurs","fri","sat","sun"]
# dayNames = ["Workday"]*7
monthNames = ["none","jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec","extra"]

# calPath = "data"
calPath = "/home/prime/sshfs/lxp/remote/isoplan/data"
mainCategory = "work"
mainCategory = "test"

showTextbox = True
# showTextbox = False
textboxFrac = 0.25

# general settings
settings = {}

# ICS calendars may use private keys that should be stored safely somewhere
# How you do that is up to you
import os
privateSettingsPath = "/home/prime/sshfs/lxp/remote/isoplan/privateSettings.py"
# create if needed
if not os.path.exists(privateSettingsPath):
    downloadIcsCalendars=[]
else:
    downloadIcsCalendars = eval(open(privateSettingsPath).read())
