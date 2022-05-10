from gameobjects import Plot,Field
import time
import logging

class GameManager:

    def __init__(self,network):
        self.logger = logging.getLogger("game")
        self.network = network
        self.actionCounter = 0
        self.lastRequestedField = None
        self.fields=[]
        self.__initState()
    
    def __initState(self):
        stateConfig = self.network.makeRequest("config.gU",{"config.gU":{}})
        self.uid=stateConfig["u"]["uId"]
        self.uname=stateConfig["u"]["uN"]
        self.loginCount=stateConfig["u"]["countLogin"]
        self.stars=stateConfig["u"]["star"]
        self.bananas=stateConfig["u"]["goldenbanana"]
        self.normalLevel=stateConfig["u"]["lvl"]
        self.normalExp=stateConfig["u"]["ep"]
        self.tropicalLevel=stateConfig["u"]["tlvl"]
        self.tropicalExp=stateConfig["u"]["tep"]
        self.registrationDate=stateConfig["u"]["regDate"]
        self.buildingStash=stateConfig["uBld"]
        self.upgradeStash=stateConfig["uUpg"]
        self.foodStash=stateConfig["uMil"]
        self.itemStash=stateConfig["uInv"]
        
        globalFavorites=stateConfig["uInvFav"]
        availableFields=stateConfig["gUp"]["ga"]
        #create field objects for all available fields
        for field in availableFields:
            gid = field["id"]
            pos = int(field["pos"])
            #bypass mushroom forest and pos 7 for now because for some reason it's showing up as available when it's not
            if pos ==  11 or pos == 7:
                continue
            #if there are favorite plants set for the field pass them to the constructor, otherwise pass an empty list
            if str(pos) in globalFavorites:
                fieldFavorites = [fav[1] for fav in globalFavorites[str(pos)].items() if fav[0] != "uId" and fav[1] != ""] 
            else:
                fieldFavorites = []
            fieldJson = self.requestField(gid,pos)
            fieldObject = Field(gid,pos,fieldJson,fieldFavorites)
            self.fields.append(fieldObject)
            self.logger.info("initialized field ("+fieldObject.toString()+")")
        #initialize the login calendar
        loginCalendar = self.network.makeRequest("dailyLoginCalendar.getConfig",{"dailyLoginCalendar.getConfig":{}})
        self.__extractCalendarInfo(loginCalendar)

    def __extractCalendarInfo(self,calendarData):
        self.giftID = 1
        for reward in calendarData["dailyLoginCalendar"]["gifts"]:
            if not "unlocked" in reward:
                self.giftID = reward["id"]
                break
        self.unlockTime = time.time()+(calendarData["dailyLoginCalendar"]["nextUnlockTime"] - calendarData["stm"])
        self.logger.info(f"next calendar gift will be available in {self.unlockTime-time.time()} seconds")

    def claimCalendar(self):
        #check if the login calendar is claimable and if it is then do so
        if self.unlockTime - time.time() < 0:
            loginCalendar = self.network.makeRequest("dailyLoginCalendar.collectGift",{"dailyLoginCalendar.collectGift":{"giftId":str(self.giftID),"forcedMonth":0}})
            self.logger.info(f"claimed day {self.giftID} calendar gift")
            self.__extractCalendarInfo(loginCalendar)
    
    def processFields(self):
        #call harvestField and sowField on all fields
        for field in self.fields:
            self.harvestField(field)
            self.sowField(field)

    def requestField(self,gid,pos):
        #request the field contents from the server
        #you can only interact with the last requested field (security measure probably) so we need to keep track
        self.lastRequestedField = pos
        fieldJson = self.network.makeRequest("field.sAG",{"field.sAG":{"gId":str(gid),"pos":str(pos)}})
        return fieldJson

    def harvestField(self,field):
        harvestedItems = {}
        beforeCounter = self.actionCounter
        harvestPacket = {"field.fia":{"q":{}}}
        
        for plot in field.plots.values():
            if plot.isHarvestable():
                name = plot.getName()
                inventID = plot.getInventID()
                harvestPacket["field.fia"]["q"][self.actionCounter]={
                    "fia":"harvest",
                    "inventID":inventID,
                    "uid":plot.plotID,
                    "fx":plot.x,
                    "fy":plot.y,
                    "angle":plot.angle,
                    "sqfId":"0",
                    "slot":"0"
                    }

                if plot.plotType == "tree":
                    harvestedAmount = 4
                elif plot.plotType == "animal" or plot.plotType == "giver" or plot.plotType == "countedgiver":
                    harvestedAmount = 1
                elif inventID == "field3":
                    harvestedAmount = 5
                elif inventID == "field2":
                    harvestedAmount = 3
                elif inventID == "field1":
                    harvestedAmount = 2

                if plot.plotType != "giver" and plot.plotType != "countedgiver" and name in self.itemStash:
                    self.itemStash[name] += harvestedAmount
                #check if the harvested item is already in the stash
                elif plot.plotType != "giver" and plot.plotType != "countedgiver" and name not in self.itemStash:
                    self.logger.warning(f"item ({name}) not found in stash")

                #increment the counter for logging purposes
                if plot.itemID in harvestedItems:
                    harvestedItems[plot.itemID] += harvestedAmount
                else:
                    harvestedItems[plot.itemID] = harvestedAmount

                self.actionCounter += 1
                
                if plot.plotType == "animal":
                    harvestPacket["field.fia"]["q"][self.actionCounter]={
                        "fia":"pamper",
                        "inventID":"dung",
                        "uid":plot.plotID,
                        "fx":plot.x,
                        "fy":plot.y,
                        "angle":plot.angle,
                        "sqfId":"0",
                        "slot":"0"
                        }
                    self.actionCounter += 1

        if self.actionCounter > beforeCounter:
            if self.lastRequestedField != field.pos:
                self.requestField(field.gid,field.pos)

            changedPlots = self.network.makeRequest("field.fia",harvestPacket)
            field.updatePlots(changedPlots)
            
            for item, amount in harvestedItems.items():
                self.logger.info(f"harvested {amount} of {item} on {field.toString()}")

    def sowField(self,field):
        sownSeeds = {}
        fedAnimals = {}
        beforeCounter = self.actionCounter
        sowPacket = {"field.fia":{"q":{}}}
        plant = field.getPlant()

        for plot in field.plots.values():
            if plot.isSowable() and plant is not None and self.itemStash[plant] > 0:
                sowPacket["field.fia"]["q"][self.actionCounter]={
                    "fia":"sow",
                    "inventID":plant,
                    "uid":plot.plotID,
                    "fx":plot.x,
                    "fy":plot.y,
                    "angle":plot.angle,
                    "sqfId":"0",
                    "slot":"0"
                    }

                #increment the counter for logging purposes
                if plant in sownSeeds:
                    sownSeeds[plant] += 1
                else:
                    sownSeeds[plant] = 1

                self.actionCounter += 1
                self.itemStash[plant] -= 1
            elif plot.isFeedable() and not plot.isIgnored():
                animal = plot.getName()
                if animal in self.foodStash and self.foodStash[animal] > 0:    
                    sowPacket["field.fia"]["q"][self.actionCounter]={
                        "fia":"sow",
                        "inventID":"feed",
                        "uid":plot.plotID,
                        "fx":plot.x,
                        "fy":plot.y,
                        "angle":plot.angle,
                        "sqfId":"0",
                        "slot":"0"
                        }
                    
                    #increment the counter for logging purposes
                    if plot.itemID in fedAnimals:
                        fedAnimals[plot.itemID] += 1
                    else:
                        fedAnimals[plot.itemID] = 1

                    self.actionCounter += 1
                    self.foodStash[animal] -= 1
                elif animal not in self.foodStash:
                    #check if food exists for the given animal
                    plot.ignore()
                    self.logger.warning(f"food for {animal} not found in mill stash")
                    
        if self.actionCounter > beforeCounter:
            if self.lastRequestedField != field.pos:
                self.requestField(field.gid,field.pos)

            changedPlots = self.network.makeRequest("field.fia",sowPacket)
            field.updatePlots(changedPlots)

            for item, amount in sownSeeds.items():
                self.logger.info(f"sown {amount} of {item} on {field.toString()}")
            for item, amount in fedAnimals.items():
                self.logger.info(f"fed {amount} of {item} on {field.toString()}")
