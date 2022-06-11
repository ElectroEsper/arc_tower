import traceback
import sys
import ac
import acsys
import os
import json

import math
import time
import timeit
import statistics

import configparser

import platform
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
#tyreChangeTime = float(config['CAR']['tyreChangeTime'])
tyreChangeTime = json.loads(config.get("CAR","tyreChangeTime"))
ac.log("{}".format(listOfActorToHide))




appName = "ARC - Tower"
mainWindow = 0


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
        ##Tyre/Stint
        ###BG
        self.stintLbl_bg = ac.addLabel(window,"")
        ac.setVisible(self.stintLbl_bg, 0)
        ac.setFontAlignment(self.stintLbl_bg, "right")
        ###Text
        self.stintLbl_txt = ac.addLabel(window,"")
        ac.setFontSize(self.stintLbl_txt, fontSize)
        ac.setVisible(self.stintLbl_txt, 0)
        ac.setFontAlignment(self.stintLbl_txt,"right")

        #Driver Status
        self.inPit = ac.addLabel(window,"")
        ac.setFontSize(self.inPit,fontSize)
        ac.setFontAlignment(self.inPit,"left")

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

        #Gates
        self.gate_current = -1
        self.gate_0 = [0, 0]
        self.gate_1 = [0, 0]
        self.gate_2 = [0, 0]
        self.gate_3 = [0, 0]
        self.gate_4 = [0, 0]
        self.gate_5 = [0, 0]
        self.gate_6 = [0, 0]
        self.gate_7 = [0, 0]
        self.gate_8 = [0, 0]

        #Tyre
        self.currentTyre = 0
        self.currentStintSinceLap = 0
        self.currentStintLenght = 0

        #Pitstops
        self.inPitLane = False
        self.pitTimerStart = 0
        self.pitTimer = 0

        self.inPitBox = False
        self.inPitBoxTimerStart = 0
        self.inPitBoxTimer = 0

        self.lastPitTime = 0
        self.pitStop = 0


# --- TOWER VAR ---
allDrivers = {}
allLabels = {}
currentSession = -1
currentSessionStrg = ''
raceOptionnalEnum = 2
trackLength = 0
nextUpdate = 0
currentUpdateTime = 0
refreshRate = 0.1
leaderboard = []
# -- LABEL VAR ---
fontSize = 20
animateSpeed = 2
longestName = 0

# -- GATES ---
gate_0 = 0
gate_1 = 0
gate_2 = 0
gate_3 = 0
gate_4 = 0
gate_5 = 0
gate_6 = 0
gate_7 = 0
gate_8 = 0
sector_1 = 0
sector_2 = 0

# -- Tyre Compound -- #
bgpath_tyre_s = None
bgpath_tyre_m = None
bgpath_tyre_h = None
tyre_icon_x = 25
tyre_icon_y = 25
##############################
##############################

verticalLbl = fontSize*1.2
#SESSION
sessionLbl_width = fontSize*2

#MODE
modeLbl_y_pos = 50
#POS
positionLbl_width = fontSize*0.33
positionLbl_left = positionLbl_width

#NAME
nameLbl_left = positionLbl_left + positionLbl_width
nameLbl_width = longestName+50

#Race optionnal
raceOptionLbl_left = nameLbl_left + nameLbl_width
## Compound
tyreCompound_width = 70+20

#Pitstop
pitstop_width = fontSize

#Size Mult
sizeMult = 1

def acMain(ac_versions):
    global mainWindow, sessionLbl_name, sessionLbl_time
    global config, sector_1, sector_2
    global gate_0, gate_1, gate_2, gate_3, gate_4, gate_5, gate_6, gate_7, gate_8
    global img_tyre_s, img_tyre_m, img_tyre_h

    main_size_x = 250
    main_size_y = 1000
    #Main
    mainWindow = ac.newApp(appName)
    ac.setSize(mainWindow, main_size_x,main_size_y)
    ac.setIconPosition(mainWindow,-10000,-10000)
    ac.setTitlePosition(mainWindow,-10000,-10000)
    #Session Time
    sessionLbl_time = ac.addLabel(mainWindow,"SESSION")
    ac.setSize(sessionLbl_time,nameLbl_left+nameLbl_width,sessionLbl_width)
    ac.setPosition(sessionLbl_time,-10,0)
    ac.setFontSize(sessionLbl_time,fontSize*2)
    ac.setFontAlignment(sessionLbl_time,"center")
    #Session name
    sessionLbl_name = ac.addLabel(mainWindow,"TEST")
    ac.setSize(sessionLbl_name,sessionLbl_name+nameLbl_width,sessionLbl_width)
    ac.setPosition(sessionLbl_name,0,-50)
    ac.setFontSize(sessionLbl_name,fontSize*2)
    ac.setFontAlignment(sessionLbl_name,"left")
    #Mode
    #modeLbl = ac.addLabel(mainWindow,"")
    #ac.setSize(modeLbl,nameLbl_width,5)
    #ac.setPosition(modeLbl,0,modeLbl_y_pos)
    #ac.setFontSize(modeLbl,fontSize*1)
    #ac.setFontAlignment(modeLbl,"center")

    #################################################
    # -- GET TRACK SETTINGS -- #
    t_track = ac.getTrackName(0)
    if t_track in config['TRACKS']:
        t_sectors = json.loads(config.get("TRACKS",t_track))
        sector_1 = t_sectors[0]
        sector_2 = t_sectors[1]
        ac.log("Setting-up for {}".format(t_track))
    else:
        t_sectors = json.loads(config.get("TRACKS","default"))
        sector_1 = t_sectors[0]
        sector_2 = t_sectors[1]
        ac.log("Setting-up as default")

    # -- SET GATES -- #
    t_sector1_section = sector_1/3
    gate_1 = t_sector1_section
    gate_2 = t_sector1_section*2
    gate_3 = sector_1
    ac.log("Gate(1-3):{}".format(gate_1,gate_2,gate_3))

    t_sector2_section = (sector_2-sector_1)/3
    gate_4 = gate_3+t_sector2_section
    gate_5 = gate_4+t_sector2_section
    gate_6 = sector_2
    ac.log("Gate(4-6):{}".format(gate_4, gate_5, gate_6))

    t_sector3_section = (1-sector_2)/3
    gate_7 = gate_6 + t_sector3_section
    gate_8 = gate_7 + t_sector3_section
    ac.log("Gate(7-8):{}".format(gate_7, gate_8))
    #################################################

    # HANDLE Sprites #
    img_tyre_s = os.path.dirname(__file__) + '/img/bg_tyre_soft.png'
    img_tyre_m = os.path.dirname(__file__) + '/img/bg_tyre_medium.png'
    img_tyre_h = os.path.dirname(__file__) + '/img/bg_tyre_hard.png'

    return appName    
def acUpdate(deltaT):
    global mainWindow, sessionLbl_name, sessionLbl_time
    global positionLbl_left, nameLbl_left, nameLbl_width, raceOptionLbl_left
    global currentSession, currentSessionStrg, trackLength
    global raceOptionnalEnum
    global nextUpdate, refreshRate, currentUpdateTime
    global config, sector_1, sector_2
    global gate_0, gate_1, gate_2, gate_3, gate_4, gate_5, gate_6, gate_7, gate_8
    global img_tyre_s, img_tyre_m, img_tyre_h, tyre_icon_x, tyre_icon_y
    global longestName

    currentUpdateTime = time.time()

    #Check if session changed...
    if currentSession != info.graphics.session:
        currentSession = info.graphics.session

    currentSession = info.graphics.session
    
    trackLength = ac.getTrackLength(0)
    if currentSession==0:
        currentSessionStrg = "FP"
    elif currentSession==1 :
            currentSessionStrg = "QUALY"
    elif currentSession==2 :
            currentSessionStrg = "LAP"



    t_mainWindow_pos_x = ac.getPosition(mainWindow)[0]
    t_mainWindow_pos_y = ac.getPosition(mainWindow)[1]
    
    #ac.setText(sessionLbl,"{}/{}".format(ac.getCarState(0,acsys.CS.LapCount),info.graphics.numberOfLaps))
    #ac.setFontAlignment(sessionLbl_time,"left")
    
    if info.graphics.numberOfLaps == 0:
        #ac.setText(sessionLbl_name,currentSessionStrg)
        ac.setText(sessionLbl_time,"{}{:02}".format(convertMillisToMinutesSeconds(info.graphics.sessionTimeLeft/1000)[0],convertMillisToMinutesSeconds(info.graphics.sessionTimeLeft/1000)[1]))
        #ac.setText(sessionLbl,"{} - {}".format(currentSessionStrg,info.graphics.sessionTimeLeft))
    else:
        ac.setText(sessionLbl_time,"{}/{}".format(ac.getCarState(findLeader(),acsys.CS.LapCount)+1,info.graphics.numberOfLaps))
    #sessionTimeLeft
    ac.setText(sessionLbl_name,currentSessionStrg)

    #How many cars?
    totalDrivers = ac.getCarsCount()
    #update driver's list
    for idx in range(totalDrivers):
        if ac.getDriverName(idx) in listOfActorToHide:
            continue
        if not idx in allDrivers.keys():
            if False:
                pass
            else:
                allDrivers.update({idx:Driver(idx)})
        if not idx in allLabels.keys():
            if False:
                pass
            else:
                allLabels.update({idx:Label(mainWindow)})
                allDrivers[idx].lblId = idx

    # SETUP LONGEST NAME #
    longestName = getLongestGame(totalDrivers)
    nameLbl_width = (longestName*(fontSize*1))
    raceOptionLbl_left = nameLbl_left + nameLbl_width
    #ac.log("{}".format(nameLbl_width))
    #Update driver's data
    for idxB in range(totalDrivers):
        
        #If a driver is on the list of people to hide...
        if ac.getDriverName(idxB) in listOfActorToHide:
            continue #Go to next driver...

        ############## Update gates ##############
        t_currentSplinePos = ac.getCarState(idxB,acsys.CS.NormalizedSplinePosition)
        t_currentGate = allDrivers[idxB].gate_current
        t_currentLap = ac.getCarState(idxB,acsys.CS.LapCount)
        if t_currentSplinePos >= 0 and t_currentSplinePos < gate_1: #If is past Start/Finish but not gate 1...
            if t_currentGate != 0: #If self.currentGate is has not been updated...
                allDrivers[idxB].gate_current = 0
                allDrivers[idxB].gate_0 = [time.time(),t_currentLap]
        elif t_currentSplinePos >= gate_1 and t_currentSplinePos < gate_2:
            if t_currentGate != 1:
                allDrivers[idxB].gate_current = 1
                allDrivers[idxB].gate_1 = [time.time(), t_currentLap]
        elif t_currentSplinePos >= gate_2 and t_currentSplinePos < gate_3:
            if t_currentGate != 2:
                allDrivers[idxB].gate_current = 2
                allDrivers[idxB].gate_2 = [time.time(), t_currentLap]
        elif t_currentSplinePos >= gate_3 and t_currentSplinePos < gate_4:
            if t_currentGate != 3:
                allDrivers[idxB].gate_current = 3
                allDrivers[idxB].gate_3 = [time.time(), t_currentLap]
        elif t_currentSplinePos >= gate_4 and t_currentSplinePos < gate_5:
            if t_currentGate != 4:
                allDrivers[idxB].gate_current = 4
                allDrivers[idxB].gate_4 = [time.time(), t_currentLap]
        elif t_currentSplinePos >= gate_5 and t_currentSplinePos < gate_6:
            if t_currentGate != 5:
                allDrivers[idxB].gate_current = 5
                allDrivers[idxB].gate_5 = [time.time(), t_currentLap]
        elif t_currentSplinePos >= gate_6 and t_currentSplinePos < gate_7:
            if t_currentGate != 6:
                allDrivers[idxB].gate_current = 6
                allDrivers[idxB].gate_6 = [time.time(), t_currentLap]
        elif t_currentSplinePos >= gate_7 and t_currentSplinePos < gate_8:
            if t_currentGate != 7:
                allDrivers[idxB].gate_current = 7
                allDrivers[idxB].gate_7 = [time.time(), t_currentLap]
        elif t_currentSplinePos >= gate_8 and t_currentSplinePos < 1:
            if t_currentGate != 8:
                allDrivers[idxB].gate_current = 8
                allDrivers[idxB].gate_8 = [time.time(), t_currentLap]

        ########################################################
        ############## Update compound ##############
        t_currentCompound = ac.getCarTyreCompound(idxB)

        if t_currentCompound != allDrivers[idxB].currentTyre: #If new compound...
            allDrivers[idxB].currentTyre = t_currentCompound
            allDrivers[idxB].currentStintSinceLap = ac.getCarState(idxB,acsys.CS.LapCount)
            allDrivers[idxB].currentStintLenght = 0
        else:
            allDrivers[idxB].currentStintLenght = ac.getCarState(idxB,acsys.CS.LapCount) - allDrivers[idxB].currentStintSinceLap
        ########################################################

        ############## FIND POSITION OF 'idxB' ##############
        #Refresh t_pos and get temporary 'driver ahead'
        t_pos = -1
        t_driver_ahead = findAhead(idxB,ac.getCarsCount())
        #ac.log("{}".format(t_driver_ahead))
        if t_driver_ahead=="None": #If driver is leader...
            t_pos = 1
        else: #If none of the above...
            t_pos = allDrivers[t_driver_ahead].currentPos+1
             
        ########################################################

        ############## IS 'idxB' in the pits ##############
        if ac.isCarInPitlane(idxB) and not allDrivers[idxB].inPitLane: #If in pitlane and inPitLane is not true...
            allDrivers[idxB].inPitLane = True #...Set inPitLane true...
            allDrivers[idxB].pitTimerStart = time.time() #...Start pitTimerStart
        elif not ac.isCarInPitlane(idxB) and allDrivers[idxB].inPitLane: #Else-if not in pitlane and inPitLane is true...
            allDrivers[idxB].inPitLane = False #...Set inPitLane false...
            allDrivers[idxB].pitTimer = time.time() - allDrivers[idxB].pitTimerStart #...update pitTimer
            allDrivers[idxB].lastPitTime = allDrivers[idxB].pitTimer #...update lastPitTime
        if allDrivers[idxB].inPitLane: #If inPitLane is true...
            allDrivers[idxB].pitTimer = time.time() - allDrivers[idxB].pitTimerStart #...update pitTimer
            ac.log("{} - Pit Timer : {}".format(idxB,allDrivers[idxB].pitTimer))
            if ac.getCarState(idxB,acsys.CS.SpeedMS)<1 and not allDrivers[idxB].inPitBox:#...if speed is < 1 mps...
                allDrivers[idxB].inPitBox = True #...assume car is in pitBox
                allDrivers[idxB].inPitBoxTimerStart = time.time()  # ...set inPitBoxTimerStart
            elif ac.getCarState(idxB,acsys.CS.SpeedMS)>=1 and allDrivers[idxB].inPitBox: #If car is moving and inPitBox...
                allDrivers[idxB].inPitBox = False #...assume car is not in pitbox
                allDrivers[idxB].inPitBoxTimer = time.time() - allDrivers[idxB].inPitBoxTimerStart
                if allDrivers[idxB].inPitBoxTimer >= tyreChangeTime: #If stayed in box long enough to change tyres...
                    allDrivers[idxB].currentStintSinceLap = ac.getCarState(idxB,acsys.CS.LapCount) #...assume tyres where changed...
                    allDrivers[idxB].pitStop += 1 #...update pitstop count...
        if allDrivers[idxB].inPitBox: #If car is in pitbox...
            allDrivers[idxB].inPitBoxTimer = time.time() - allDrivers[idxB].inPitBoxTimerStart  # ...update inPitBoxTimer



        ########################################################
        t_lbl_id = allDrivers[idxB].lblId #Fetch driver's label id
        t_label = allLabels[t_lbl_id] #Fetch label from id
        t_carAhead = t_driver_ahead #setup updated car ahead
        t_pos_y = (t_pos*verticalLbl)+modeLbl_y_pos+1
       
        #Get labels
        t_posLbl = t_label.posLbl
        t_nameLbl = t_label.nameLbl
        t_intervalLbl = t_label.intervalLbl
        t_gapToLeadLbl = t_label.gapToLeadLbl
        t_stintLbl_bg = t_label.stintLbl_bg
        t_stintLbl_txt = t_label.stintLbl_txt
        t_pitstopLbl = t_label.inPit
        #animate on position change
        if t_pos != allDrivers[idxB].currentPos: #If position changed.
            allDrivers[idxB].currentPos = t_pos
            t_label.destinationPosition = [positionLbl_left,t_pos_y]
            t_label.animate = True
        if t_label.animate:
            animatePosMove(t_label)

        #Set position
        #ac.setPosition(t_posLbl,positionLbl_left,t_pos_y)    
        t_Lbl_y = ac.getPosition(t_posLbl)[1]
        ac.setText(t_posLbl,"{}".format(t_pos))
        ac.setFontAlignment(t_posLbl,"right")
        
        #Set name
        ac.setPosition(t_nameLbl,nameLbl_left,t_Lbl_y)
        #ac.setSize(t_nameLbl,nameLbl_width-100,fontSize)
        ac.setText(t_nameLbl,"{}".format(getLastName(ac.getDriverName(idxB))))
        ac.setFontAlignment(t_nameLbl,"left")

        if raceOptionnalEnum == 0: #If raceoptionnal is intervals...
            ac.setVisible(t_intervalLbl,1)
            t_carChaserCurrentLap = ac.getCarState(idxB,acsys.CS.LapCount)
            ac.setPosition(t_intervalLbl,raceOptionLbl_left,t_Lbl_y)
            if currentUpdateTime >= nextUpdate:
                #ac.log("TRUE")
                if t_carAhead == "None":
                    t_carAheadCurrentLap = -1 
                else:
                    t_carAheadCurrentLap = ac.getCarState(t_carAhead,acsys.CS.LapCount)
                if  t_carAhead != "None" and (t_carAheadCurrentLap-t_carChaserCurrentLap > 1): #If lapped
                    ac.setText(t_intervalLbl,"+{} L".format((t_carAheadCurrentLap-t_carChaserCurrentLap)))
                elif t_carAhead != "None":  
                    #intervalToLabel(t_intervalLbl,t_carAhead,ac.getCarState(t_carAhead,acsys.CS.NormalizedSplinePosition),idxB,ac.getCarState(idxB,acsys.CS.NormalizedSplinePosition),(ac.getCarState(idxB,acsys.CS.SpeedMS)+ac.getCarState(t_carAhead,acsys.CS.SpeedMS))/2)
                    intervalToLabel_gate(t_intervalLbl, idxB, t_carAhead)
                else:
                    ac.setText(t_intervalLbl,"INTERVAL")
                ac.setFontAlignment(t_intervalLbl,"right")
        else:
            ac.setVisible(t_intervalLbl,0)
        if raceOptionnalEnum == 1: #If raceoptionna is gap to leader
            ac.setVisible(t_gapToLeadLbl,1)
            #ac.setText(modeLbl,"INTERVAL")
            t_carChaserCurrentLap = ac.getCarState(idxB,acsys.CS.LapCount)
            ac.setPosition(t_gapToLeadLbl,raceOptionLbl_left,t_Lbl_y)
            if currentUpdateTime >= nextUpdate:
                #ac.log("TRUE")
                if t_carAhead == "None":
                    t_carAheadCurrentLap = -1 
                else:
                    t_carAheadCurrentLap = ac.getCarState(findLeader(),acsys.CS.LapCount)
                if  t_carAhead != "None" and (t_carAheadCurrentLap-t_carChaserCurrentLap > 1): #If lapped
                    ac.setText(t_gapToLeadLbl,"+{} L".format((t_carAheadCurrentLap-t_carChaserCurrentLap)))
                elif t_carAhead != "None": 
                    t_carAhead = findLeader()
                    if allDrivers[idxB].gate_current == -1:
                        pass
                    else:
                        intervalToLabel_gate(t_gapToLeadLbl,idxB,t_carAhead)
                else:
                    ac.setText(t_gapToLeadLbl,"LEADER")
                ac.setFontAlignment(t_gapToLeadLbl,"right")
        else:
            ac.setVisible(t_gapToLeadLbl, 0)
        if raceOptionnalEnum == 2:
            ac.setVisible(t_stintLbl_bg, 1)
            ac.setVisible(t_stintLbl_txt,1)
            ac.setPosition(t_stintLbl_txt,raceOptionLbl_left,t_Lbl_y)
            ac.setPosition(t_stintLbl_bg, raceOptionLbl_left - tyreCompound_width, t_Lbl_y+3)
            #ac.setText(t_stintLbl,"test")
            if currentUpdateTime >= nextUpdate:
                t_currentTyre = allDrivers[idxB].currentTyre
                ac.setText(t_stintLbl_txt, "{} Laps".format(allDrivers[idxB].currentStintLenght))
                #ac.log("{}".format(t_currentTyre))
                t_currentStingLenght = allDrivers[idxB].currentStintLenght
                if t_currentTyre == "S":
                    ac.setBackgroundTexture(t_stintLbl_bg, img_tyre_s)
                    ac.setSize(t_stintLbl_bg, tyre_icon_x * (fontSize / tyre_icon_x), tyre_icon_y * (fontSize / tyre_icon_y))
                elif t_currentTyre == "M":
                    ac.setBackgroundTexture(t_stintLbl_bg, img_tyre_m)
                    ac.setSize(t_stintLbl_bg, tyre_icon_x * (fontSize / tyre_icon_x), tyre_icon_y * (fontSize / tyre_icon_y))
                elif t_currentTyre == "H":
                    ac.setBackgroundTexture(t_stintLbl_bg, img_tyre_h)
                    ac.setSize(t_stintLbl_bg, tyre_icon_x * (fontSize / tyre_icon_x), tyre_icon_y * (fontSize / tyre_icon_y))
                else:
                    ac.setBackgroundTexture(t_stintLbl_bg,"")
        else:
            ac.setVisible(t_stintLbl_bg,0)
            ac.setVisible(t_stintLbl_txt,0)

        if allDrivers[idxB].inPitLane and ac.isConnected(idxB):
            ac.setVisible(t_pitstopLbl,1)
            ac.setPosition(t_pitstopLbl,raceOptionLbl_left+pitstop_width,t_Lbl_y)
            ac.setText(t_pitstopLbl,"P")
        elif not ac.isConnected(idxB):
            ac.setVisible(t_pitstopLbl, 1)
            ac.setPosition(t_pitstopLbl, raceOptionLbl_left + pitstop_width, t_Lbl_y)
            ac.setText(t_pitstopLbl, "D")
        else:
            ac.setVisible(t_pitstopLbl,0)


    if currentUpdateTime >= nextUpdate:        
        nextUpdate = time.time() + refreshRate

##############################
##############################

def findLeader():
    
    try:
        leader = 0
        for i in range(ac.getCarsCount()):
            carPos = ac.getCarLeaderboardPosition(i)
            if carPos == 1:
                leader = i
                return leader
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.log("Error @ findLeader()")
        ac.log("{}".format(traceback.format_exception(exc_type, exc_value, exc_traceback)))
def findAhead(source, carCount):
        try:
             #Set default variables
            ahead = 0
            offset = 1
            maxAttempt = carCount
            attempt = 0
            #Find source car's position for reference
            s_pos = ac.getCarRealTimeLeaderboardPosition(source)+1
            #ac.log("CC:{}".format(carCount))
            if (s_pos-1) > 0: #If source car's position -1 is 0, then that car is in first...
                while True:
                    for i in range(carCount): #For each cars...
                        i_pos = ac.getCarRealTimeLeaderboardPosition(i)+1 #Get "i"'s position on the leaderboard (+1 to get real position) 
                        if i_pos == (s_pos-offset): #If "i"'s position is equal to source-car's position minus current offset...
                            if ac.getDriverName(i) in listOfActorToHide: #If "i" is a car that must be ignored (eg. ARC-TV)...
                                offset += 1 #Increase the offset by one...
                            else:
                                ahead = i #We found our guy!
                                return ahead #Return it and carry on...
                        elif (s_pos-offset) <= 0:
                            return "None"
                    attempt += 1
            return "None" #Source-car is in first, what else do you what from me?         
        except :
            #In-case shit hits the fan, I wanna know why!
            exc_type, exc_value, exc_traceback = sys.exc_info()
            ac.log("Error @ findAhead()")
            ac.log("{}".format(traceback.format_exception(exc_type, exc_value, exc_traceback)))              
def getLastName(input):
    lastName = ''
    try:
        words = input.split()
        size = len(words)
        lastName = words[size-1].upper()
        return lastName
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.log("Error @ getLastName()")
        ac.log("{}".format(traceback.format_exception(exc_type, exc_value, exc_traceback)))        
def intervalToLabel(label,from_id,from_pos,to_id,to_pos,speedAvg):
    t_from_lap = ac.getCarState(from_id,acsys.CS.LapCount)
    t_to_lap = ac.getCarState(to_id,acsys.CS.LapCount) 
    t_dist = from_pos-to_pos
    
    if t_from_lap > t_to_lap and to_pos<1: #If ahead car on the next lap...
        t_dist = from_pos+(1-to_pos)
        if t_dist > 1:
            t_dist = from_pos
        #ac.log("From@{}: {:.3f}, To@{}: {:.3f}, Dist:{:.3f}".format(ac.getCarRealTimeLeaderboardPosition(from_id),round(from_pos,3),ac.getCarRealTimeLeaderboardPosition(to_id),round(to_pos,3),round(t_dist,3)))
    elif t_from_lap == t_to_lap and to_pos>from_pos: #if ahead car got pass while both on same lap...
       t_dist = to_pos - from_pos
    #if to_pos>from_pos and from_pos<1 and to_pos<1: #If ahead car was passed
    #   t_dist = to_pos - from_pos
    distance = t_dist*trackLength
    #ac.log("{}".format(distance))
    if speedAvg < 15:
        speedAvg = 15
    intervalTime =  distance/speedAvg
    #intervalTime =  distance
    ac.setText(label,"{:+.1f}".format(intervalTime))
def animatePosMove(label):
    try:
        t_label = label.posLbl
        t_destinationPosition = label.destinationPosition
        t_position = ac.getPosition(t_label)
        
        if t_destinationPosition[1] > t_position[1] : #If destination is lower than current
            t_diff = t_destinationPosition[1] - t_position[1]
            #ac.log("{}".format(t_diff)) 
            if t_diff == 0:
                label.animate = False
            elif t_diff < animateSpeed:
                ac.setPosition(t_label,t_destinationPosition[0],t_destinationPosition[1])
                label.animate = False
            else:
                ac.setPosition(t_label,t_position[0],t_position[1]+animateSpeed)
        elif t_destinationPosition[1] < t_position[1] : #If destination is higher than current
            t_diff = t_position[1] - t_destinationPosition[1]
            #ac.log("{}".format(t_diff)) 
            if t_diff == 0:
                label.animate = False
            elif t_diff < animateSpeed:
                ac.setPosition(t_label,t_destinationPosition[0],t_destinationPosition[1])
                label.animate = False
            else:
                ac.setPosition(t_label,t_position[0],t_position[1]-animateSpeed)
        else:
            label.animate = False
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.log("Error @ animatePosMove()")
        ac.log("{}".format(traceback.format_exception(exc_type, exc_value, exc_traceback)))
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
def intervalToLabel_gate(label,from_id,to_id):
    try:
        t_from_gate = allDrivers[from_id].gate_current
        t_from_gate_arr = getGateValueOfCar(from_id,t_from_gate)
        t_from_gate_time = t_from_gate_arr[0]
        t_from_gate_lap = t_from_gate_arr[1]

        t_ahead_gate_arr = getGateValueOfCar(to_id,t_from_gate)
        t_ahead_gate_time = t_ahead_gate_arr[0]
        t_ahead_gate_lap = t_ahead_gate_arr[1]

        if t_from_gate_lap == t_ahead_gate_lap: #If cars are on the same lap...
            ac.setText(label,"{:+.1f}".format(t_from_gate_time-t_ahead_gate_time))
        else: #Otherwise they are not on the same lap...
            ac.setText(label,"{} L".format(t_ahead_gate_lap-t_from_gate_lap))
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.log("Error @ intervalToLabel_gate()")
        ac.log("{}".format(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    pass
def getGateValueAheadCar(ahead_id,gateNumber):
    string = ("gate_" + str(gateNumber))
    return getattr(allDrivers[ahead_id],string)
def getGateValueOfCar(id,gateNumber):
    try:
        string = ("gate_" + str(gateNumber))
        return getattr(allDrivers[id],string)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.log("Error @ getGateValueOfCar()")
        ac.log("{}".format(traceback.format_exception(exc_type, exc_value, exc_traceback)))
def getLongestGame(carCount):
    try:
        t_longestName = 0
        for i in range(carCount):
            t_lenght = len(getLastName(ac.getDriverName(i)))
            if t_lenght > t_longestName:
                t_longestName = t_lenght
        ac.log("Longest Name : {}".format(t_longestName))
        return t_longestName
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ac.log("Error @ getLongestGame()")
        ac.log("{}".format(traceback.format_exception(exc_type, exc_value, exc_traceback)))