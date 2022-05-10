import time

class Plot():
    def __init__(self,plotID,itemID,plotType,x,y,size,angle,dung,start,end,serverTime):
        self.plotID = plotID
        self.itemID = itemID
        self.plotType = plotType
        self.x = x
        self.y = y
        self.size = size
        self.angle = angle
        self.dung = dung
        self.start = start
        self.end = end
        self.serverTime = serverTime
        self.localTime = time.time()
        self.ignored = False
    
    def ignore(self):
        self.ignored = True

    def isIgnored(self):
        return self.ignored

    def isHarvestable(self):
        if self.start != 0 and self.end != 0 and self.serverTime + time.time() - self.localTime > self.end:
            return True
        return False
    
    def getInventID(self):
        if self.plotType == "plant":
            if self.size == 4:
                return "field3"
            elif self.size == 3:
                return "field2"
            elif self.size == 2:
                return "field1"
        else:
            return self.itemID

    def getName(self):
        name = self.itemID.split("_")[0]
        return name

    def isSowable(self):
        if self.plotType == "field":
            return True
        return False

    def isFeedable(self):
        if self.plotType == "animal" and not self.dung and self.start == 0 and self.end == 0:
            return True
        return False



class Field():
    NORMAL=0
    GREEN_MEADOW=1
    PARK=2
    BAHAMARAMA=3
    MAGICAL_GLADE=4
    HAUNTED_MANOR=10
    MUSHROOM_FOREST=11


    def __init__(self,gid,pos,fieldJson,favorites):
        self.gid = gid
        self.pos = pos
        self.plant=None
        self.favorites = favorites
        self.plots = {}
        self.updatePlots(fieldJson)

    def updatePlots(self,fieldJson):
        if "gaF" not in fieldJson or isinstance(fieldJson["gaF"],list):
            return
        for plot in fieldJson["gaF"].values():
            ignore = plot["fId"] in self.plots and self.plots[plot["fId"]].isIgnored()
            self.plots[plot["fId"]] = Plot(
                plotID=str(plot["fId"]),
                itemID=str(plot["id"]),
                plotType=str(plot["typ"]),
                x=str(plot["fX"]),
                y=str(plot["fY"]),
                size=int(plot["sX"])+int(plot["sY"]),
                angle=str(plot["ang"]),
                dung=bool(int(plot["du"])),
                start=int(plot["st"]),
                end=int(plot["ed"]),
                serverTime=int(fieldJson["stm"])
                )
            if ignore:
                self.plots[plot["fId"]].ignore()
    
    def getPlant(self):
        if self.plant is not None:
            return self.plant
        elif len(self.favorites) > 0:
            return self.favorites[0]

    def setPlant(self,plantName):
        self.plant = plantName

    def toString(self):
        if self.pos == Field.NORMAL:
            return "main farm"
        elif self.pos == Field.GREEN_MEADOW:
            return "green meadow"
        elif self.pos == Field.PARK:
            return "park"
        elif self.pos == Field.BAHAMARAMA:
            return "bahamarama"
        elif self.pos == Field.MAGICAL_GLADE:
            return "magical glade"
        elif self.pos == Field.HAUNTED_MANOR:
            return "haunted manor"
        elif self.pos == Field.MUSHROOM_FOREST:
            return "mushroom forest"
        else:
            return "unknown field pos: "+str(self.pos)

    def isEmpty(self):
        if len(self.plots) == 0:
            return True
        return False


