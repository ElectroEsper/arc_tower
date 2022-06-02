import sys
import math
import os
import platform
import acsys
import traceback
import ac
import time
import configparser

if platform.architecture()[0] == '64bit':
	sysdir=os.path.dirname(__file__)+'/stdlib64'
else:
	sysdir=os.path.dirname(__file__)+'/stdlib'
sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."

import ctypes
from sim_info_lib.sim_info import info


# HANDLE .INI File #
#configfile = os.path.join(os.path.dirname(__file__), 'arc_tower.ini')
configfile = "apps\\python\\arc_tower\\arc_tower.ini"
ac.log("{}".format(configfile))
config = configparser.ConfigParser()
config.read(configfile)
#config.read('arc_tower.ini')
listOfActorToHide = config['CASTER']['toHide']
ac.log("{}".format(listOfActorToHide))




appName = "ARC - Tower"
mainWindow = 0

def convertMillisToSecondsMillis(millis):
    seconds = millis
    return seconds
def convertMillisToMinutesSecondsMillis(millis):
    minutes = math.floor(millis/60)
    raw_seconds = math.floor(millis)
    seconds = millis - (minutes*60)
    seconds = round(seconds,3)
    return minutes,seconds
def convertMillisToMinutesSeconds(millis):
    minutes = math.floor(millis/60)
    raw_seconds = math.floor(millis)
    seconds = millis - (minutes*60)
    seconds = math.floor(seconds)
    if minutes > 60:
        floored_minutes = math.floor(minutes/60)
        seconds = minutes - (floored_minutes*60)
        minutes = "{}h".format(floored_minutes)
    else:
        minutes = "{}:".format(minutes)
    return minutes,seconds

class Label:
    def __init__(self,window):

        #Animation related
        self.animate = False
        self.originalPosition = [0,0]
        self.destinationPosition = [0,0]

        #Pos
        self.posLbl = ac.addLabel(window,"")
        ac.setFontSize(self.posLbl,fontSize)
        #Badge

        #Name
        self.nameLbl = ac.addLabel(window,"")
        ac.setFontSize(self.nameLbl,fontSize)

        #Race optionnals
        ##Interval
        self.intervalLbl = ac.addLabel(window,"")
        ac.setFontSize(self.intervalLbl,fontSize)
        ac.setVisible(self.intervalLbl,0)
        ##Gap to leader
        self.gapToLeadLbl = ac.addLabel(window,"")
        ac.setFontSize(self.gapToLeadLbl,fontSize)
        ac.setVisible(self.gapToLeadLbl,0)
class Driver:
    def __init__(self,id):
        self.startPosition = -1
        self.currentPos = -1
        self.driverAheadId = -1

        self.lblId = 0

        #Self data
        self.id=id
        self.CompletedLap = -1
        self.LastLapCompletedAtTime = 0
        self.LastLapStartedAtTime = 0

        self.LastLap = 0

        self.inSector1 = 0
        self.inSector2 = 0
        self.inSector3 = 0

        self.pb_s1 = 9999999
        self.pb_s2 = 9999999
        self.pb_s3 = 9999999
        self.pb_lap = 9999999
