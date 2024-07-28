#Will Miller
#Script to read Amateur competitor data from BallroomCompExpress and calculate placements

import re
import classes
import helper
import datetime

#These are all the key value pairs for dance information in BallroomCompExpress
age = {1: "Adult", 2: "Senior I", 3: "Senior II", 4: "Senior III", 5: "Senior IV",
            6: None, 7: "Pre-Teen", 8: "Pre-Teen II", 9: "Junior I", 10: "Junior II",
            11: "Youth", 12: "Under 21", 13: "Senior V", 14: "Open", 15: "Adult A1",
            16: "Adult A2", 17: None, 18: "Adult B1", 19: "Adult B3", 20: "Adult B2",
            21: "Adult C1", 22: "Adult C2", 23: "Adult C3", 24: "Adult D1", 25: "Adult D2",
            26: "Adult D3", 27: "Adult A", 28: "Adult B", 29: "Adult C", 30: "Adult D",
            31: "Adult", 32: "All Ages", 33: "Teddy-Bear"
    }
level = {1: "Newcomer", 2: "Bronze", 3: "Silver", 4: "Gold", 5: "Novice",
        6: "Pre-Champ", 7: "Championship", 8: "Syllabus", 9: "Open", 10: "Pre-Bronze",
        11: "Intermediate Bronze", 12: "Full Bronze", 13: "Open Bronze", 14: "Advanced Bronze", 15: "Pre-Silver",
        16: "Intermediate Silver", 17: "Full Silver", 18: "Open Silver", 19: "Advanced Silver", 20: "Pre-Gold",
        21: "Intermediate Gold", 22: "Full Gold", 23: "Open Gold", 24: "Advanced Gold", 25: "Open Scholarship",
        26: "Master of Syllabus", 27: "Closed Syllabus", 28: "Open Syllabus"
}
category = {1: "Professional", 2: "Amateur", 3: "Pro/Am Leaders", 4: "T/S Leaders", 5: "Solo Leaders",
        6: "Solo Followers", 7: None, 8: None, 9: "Switch-Role", 10: "Mixed Proficiency Leaders",
        11: "Rookie-Vet", 12: "Pro/Am Followers", 13: "T/S Followers", 14: "Mixed Proficiency Followers", 15: "WDSF",
}
style = {
    1: "International Standard", 2: "International Latin", 3: "International", 4: "American Smooth", 5: "American Rhythm",
    6: "American", 7: None, 8: "Club", 9: "Country"
}

#The dates on the website have ranges and commas that need to be taken out to convert to date objects
def cleanDate(webDate: str): 
    formattedDate = re.sub("-.*?,", "", webDate)
    formattedDate = formattedDate.replace(',', '')
    data = formattedDate.split()
    finalDate = datetime.datetime(int(data[2]), helper.monthToInt(data[0]), int(data[1]))
    return finalDate

#test function to work with div data which will help reimplement scrapeEvent
#><div class="event-entry category3 age5 level15 style5 special1"><a href="./results.php?cid=115&eid=6780">
def getEventData(eventEntryString: str):
    if isinstance(eventEntryString, str) == False:
        print("getDances() paramaeter must be a string with the event name. EX: \"Amateur Adult Silver W/T/F")
        return None
    values = eventEntryString.split()
    return [category[int(values[1][len("category"):])],  age[int(values[2][len("age"):])], level[int(values[3][len("level"):])], style[int(values[4][len("style"):])]]

def getURL(cid=None, eid=None):
    baseURL = "http://ballroomcompexpress.com"
    if cid == None:
        return baseURL
    elif(eid == None):
        return baseURL + "/results.php?cid=" + str(cid)
    else:
        return baseURL + "/results.php?cid=" + str(cid) + "&eid=" + str(eid)

#def scrapeBallroomCompExpress()

#creates a file with the list of recent competitions on the ballroomcompexpress website
#It will add on to the file. So it is possible to keep information on comps no longer on the recent comps list.
def scrapeRecentComps():
    filename = "recentcomps.csv"
    #Open webpage and get string text
    pageString = helper.getWebPage(getURL())[0]
    if type(pageString) != str:
        print("Error scrapeRecentComps(): " + getURL()+ " failed to open")
        return None
    #Get all the text involving only the comps that have already occurred
    startIndex = pageString.find("<h2>Recent Comps</h2>") + len("<h2>Recent Comps</h2>")
    endIndex = pageString.find("</div></div>", startIndex)
    recentCompsList = pageString[startIndex:endIndex]
    #Get comp CID's
    cidStrings = re.findall("cid=.*?\'", recentCompsList)
    cidList = []
    for string in cidStrings:
        cidList.append(int(string[4:-1]))
    #Get comp Information
    compNames = re.findall("<span class=\"label\">.*?</div>", recentCompsList)
    index = 0
    listOfComps = []
    try:
        #read current file and get list of known cid's
        f = open(filename,"r")
        knownCids = []
        lineNum = 1
        for line in f:
            if lineNum != 1: #Skip the headers of the columns
                try:
                    values = line.split(',')
                    cid = int(values[0])
                    knownCids.append(cid) # datetime.datetime(int(data[2]), monthToInt(data[0]), int(data[1]))
                    dateParts = values[2].split('/')
                    listOfComps.append(classes.Comp(cid, values[1], datetime.datetime(int(dateParts[1]), int(dateParts[0]), int(dateParts[2])), values[3], values[4]))
                except:
                    print(f'scrapeRecentComps(): Failed to capture cid in {filename} on line {lineNum}')
            lineNum += 1
        f.close() 
        recentCompFile = open(filename, "a")
        while index < len(compNames):
            compNames[index] = re.sub("<br>", "--", compNames[index])
            compNames[index] = re.sub("<.*?>", "", compNames[index])
            compInfo = compNames[index].split("--")
            cityState = compInfo[2].split(", ")
            if cidList[index] not in knownCids:
                recentCompFile.write(str(cidList[index]) + ',' + compInfo[0].strip() + ',' + cleanDate(compInfo[1]).strftime("%x") + ',' + cityState[0] + ',' + cityState[1] + '\n')
                listOfComps.append(classes.Comp(cidList[index], compInfo[0].strip(), cleanDate(compInfo[1]), cityState[0], cityState[1]))
            index += 1
        recentCompFile.close()
    except IOError:
        recentCompFile = open(filename, "w")
        recentCompFile.write("cid,comp_name,date,city,state\n")
        while index < len(compNames):
            compNames[index] = re.sub("<br>", "--", compNames[index])
            compNames[index] = re.sub("<.*?>", "", compNames[index])
            compInfo = compNames[index].split("--")
            cityState = compInfo[2].split(", ")
            recentCompFile.write(str(cidList[index]) + ',' + compInfo[0].strip() + ',' + cleanDate(compInfo[1]).strftime("%x") + ',' + cityState[0] + ',' + cityState[1] +'\n')
            listOfComps.append(classes.Comp(cidList[index], compInfo[0].strip(), cleanDate(compInfo[1]), cityState[0], cityState[1]))
            index += 1
        recentCompFile.close()
    return listOfComps

#Grabs all the events that match requirements and their eid's so we can traverse the website and check the results of each event
#args are strings that act as filters. If you don't want something like "Rookie-Vet" add "!Rookie-Vet" as an arg

def scrapeComp(cid, fileName, *argv):
    #open webpage
    pageString = helper.getWebPage(getURL(cid))[0]
    if type(pageString) != str:
        print("Error scrapeComp(): " + getURL(cid)+ " failed to open")
        return None
    #Extact useful data
    eventData = pageString[pageString.find("<div class=\"clear\"></div>"):pageString.rfind("<!-- Footer -->")]
    allEvents = re.findall("event-entry .*?\">", eventData)
    
    allEIDs = re.findall("eid=.*?\">", eventData, flags=re.ASCII)
    eidList = []
    listOfEvents = []
    for eid in allEIDs:
        eidList.append(int(eid[4:-2]))
    compName = pageString[pageString.find("<h1>") + len("<h1>Results for "):pageString.find("</h1>")]
    for i in range(0, len(allEvents)):
        allEvents[i] = getEventData(allEvents[i])
    
    i = 0
    while i < len(allEvents):
        flag = False
        for arg in argv:
            if type(arg) != str:
                print("Error scrapeComp(): args must be of type str")
                return
            else:
                if arg[0] == '!':
                    temp = arg[1:] #Cutting off the not operator
                    flag = temp in allEvents[i]
                else:
                    flag = arg not in allEvents[i]
                if flag:
                    allEvents.pop(i)
                    i -= 1
                    break
        if  flag or allEvents[i] == "": #if allEvents[i] == "" -> That is a team match which is being ignored
            eidList.pop(i)
            allEvents.pop(i)
        else:
            i += 1
    file = open(fileName, "w")
    print("Writing to File: " + fileName)
    file.write(compName + '\n')
    remaining = len(eidList)
    print("Total Events: " + str(remaining))
    i = 0
    for eid in eidList:
        # Add step so we can get the event meta data from the comp page and not the event page
        eventMetaData = allEvents[i]
        event = scrapeEvent(cid, eid)
        listOfEvents.append(classes.Event(eid, eventMetaData[0], eventMetaData[1], eventMetaData[2], eventMetaData[3], event[1], event[0], cid))
        file.write(listOfEvents[-1].toString())
        remaining -=1
        print(str(eid) + " Captured (" + str(remaining) + " left)")
        i += 1
    file.close()
    return listOfEvents
    # def __init__(self, eid:int, category: str, age: str, level: str, style: str, dances: str, entries: list, cid: int): #Key in dicionary is EID

#There is a format assumption on the name of the event
# style1 and style2 are two words that makeup the name of the style EX: Int. Latin
#Amateur <age> <level> <style1> <style2> <dance> 
#TODO: This function is essentially useless. Fix with some fuzzy string matching
def getCompCid(compName):
    if type(compName) != str:
        print("Error getCompCid(): compName must be a str")
        return None
    if compName == "":
        print("Error getCompCid(): compName cannot be empty")
        return None
    file = open("recentcomps.csv", "r")
    fileText = file.read()
    file.close()
    while fileText.find('\n') != -1:
        line = fileText[0 : fileText.find('\n')]
        fileText = fileText[fileText.find('\n') + 1:]
        data = line.split(" | ")
        if data[1] == compName:
            return int(data[0])
    #TODO: Add functionality that if the name cannot be found to update the comp file with new comps
    
def scrapeEvent( cid: int, eid: int):
    #open and get webpage
    pageString = helper.getWebPage(getURL(cid, eid))[0]
    if type(pageString) != str:
        print("Error scrapeEvent(): " + getURL(cid, eid)+ " failed to open")
        return None
    #Cutting excess information
    startIndex = pageString.find("Results for ") + len("Results for ")
    endIndex = pageString.find('<', startIndex)
    #Pulling event title
    titleName = pageString[startIndex:endIndex]
    titleTokens = titleName.split()
    #Getting results
    results = getCoupleOrder(pageString)
    eidToName = getCoupleNames(pageString)
    coupleResults = []
    #Creating entries for event object
    for key in results.keys():
        couple = eidToName[key]
        entry = classes.Entry(key, couple[0], couple[1], results[key][0], results[key][1], eid)
        coupleResults.append(entry)
    return (coupleResults, titleTokens[-1]) #The last title token is the dances (list of classes.Entry, str)

#Used by scrapeEvent() to get dictionary of entrantID's with corresponding lead and follow names
def getCoupleNames(pageString: str):
    startOfCoupleData = pageString.find("var dancers = ")
    coupleData = pageString[startOfCoupleData:pageString.find(");",startOfCoupleData)]
    startOfEventName = pageString.find("</script><h1>", startOfCoupleData)
    nameOfEvent = pageString[startOfEventName + len("</script><h1>results for "):pageString.find("</h1>", startOfEventName)].lower()
    eidDict = {}
    index = 0
    eidValues = re.findall('entrantid.*?,', coupleData)
    leaderFnames = None
    leaderLnames = None
    followerFnames =None
    followerLnames = None
    if nameOfEvent.find("solo") == -1: 
        leaderFnames = re.findall('leaderfname.*?,', coupleData)
        leaderLnames = re.findall('leaderlname.*?,', coupleData)
        followerFnames = re.findall('followerfname.*?,', coupleData)
        followerLnames = re.findall('followerlname.*?,', coupleData)
    else:
        if nameOfEvent.find("follow") != -1: #Follower's solo proficiency event
            followerFnames = re.findall('fname.*?,', coupleData)
            followerLnames = re.findall('lname.*?,', coupleData)
        else:
            leaderFnames = re.findall('fname.*?,', coupleData)
            leaderLnames = re.findall('lname.*?,', coupleData)
    for eid in eidValues:
        intEid = int(eid[eid.find(':') + 3: eid.rfind('\\\"')])
        leaderName = None
        followerName = None
        try:
            lFname = leaderFnames[index]
            lLname = leaderLnames[index]
            leaderName = lFname[lFname.find(':') + 3: lFname.rfind('\\\"')].strip() + " " + lLname[lLname.find(':') + 3: lLname.rfind('\\\"')].strip()
        except:
            leaderName = ""
        try:
            fFname = followerFnames[index]
            fLname = followerLnames[index]
            followerName = fFname[fFname.find(':') + 3: fFname.rfind('\\\"')].strip() + " " + fLname[fLname.find(':') + 3: fLname.rfind('\\\"')].strip()
        except:
            followerName = ""
        eidDict[intEid] = [leaderName, followerName]
        index += 1
    return eidDict

#Used by scapeEvent() to get dictionary of entrantID: [placement, cut]
def getCoupleOrder(pageString: str):
    #cut is the name for the subevents -> final, semi, quarter, ...
    data = pageString[pageString.find("partnershiporder"):pageString.find("Final")]
    cutNames = ["Final"]
    designations = re.findall("designation\":\".*?\"", data)
    index = len(designations) - 1
    while index >= 0:
        currDes = designations[index]
        currDes = currDes[currDes.find(":\"") + 2:currDes.rfind("\"")]
        cutNames.append(currDes)
        index -= 1
    orders = re.findall('partnershiporder.*?]', data)
    index = 0
    rank = {}
    placement = 1
    for order in orders:
        orders[index] = order[order.find("[") + 1:order.find("]")]
        index+=1
    
    cutNum = len(orders) - 1
    cutsChecked = 0
    while cutNum >= 0:
        index = 0
        cut = orders[cutNum]
        idList = cut.split(',')
        while index < len(idList):
            if int(idList[index]) not in rank:
                rank[int(idList[index])] = [placement, cutNames[cutsChecked]]
                placement += 1
                
            index += 1
        cutNum -= 1
        cutsChecked += 1
    return rank

#TODO: Add the partner as part of the information given about a person's results
def getDancerPlacement(cid, eid, name, isLead=True):
    pageString = helper.getWebPage(getURL(cid, eid))[0]
    if type(pageString) != str:
        print("Error getDancerPlacement(): " + getURL(cid, eid)+ " failed to open")
        return None
    if isLead:
        dancerName = name.split()
        searchFirst = "leaderfname\\\":\\\"" + dancerName[0]
        searchLast = "leaderlname\\\":\\\"" + dancerName[1]
        if pageString.find(searchLast) ==  -1 or pageString.find(searchFirst) == -1:
            return None
    else:
        dancerName = name.split()
        searchFirst = "followerfname\\\":\\\"" + dancerName[0]
        searchLast = "followerlname\\\":\\\"" + dancerName[1]
        if pageString.find(searchLast) == -1 or pageString.find(searchFirst) == -1:
            return None

    #Cutting excess information
    startIndex = pageString.find("Results for ") + len("Results for ")
    endIndex = pageString.find('<', startIndex)
    #Pulling event title
    title = pageString[startIndex:endIndex]
    titleNameSplit = title.split()
    titleName = titleNameSplit[0]
    for i in range(1, len(titleNameSplit)):
        titleName = titleName + " " + titleNameSplit[i]
    #search through pageString to find a matching name with entrantID
    #entrantIndex serves as a flag that there are more entrants
    entrantIndex = pageString.find("entrantid")
    #Search index keeps track of where in the page we are so we do not keep traversing through old info
    searchIndex = entrantIndex + len("entrantid\\\":\\\"")
    fName = None
    lName = None
    entrantID = None
    while entrantIndex != -1:
        entrantID = int(pageString[searchIndex:pageString.find("\\", searchIndex)])
        searchIndex = pageString.find("\\", searchIndex)
        if isLead:
            startIndex = pageString.find("leaderfname", searchIndex) + len("leaderfname\\\":\\\"")
            endIndex = pageString.find("\\\"", startIndex)
            searchIndex = endIndex
            fName = pageString[startIndex:endIndex].strip()
            startIndex = pageString.find("leaderlname", searchIndex) + len("leaderlname\\\":\\\"")
            endIndex = pageString.find("\\\"", startIndex)
            searchIndex = endIndex
            lName = pageString[startIndex:endIndex].strip()
        else:
            startIndex = pageString.find("followerfname", searchIndex) + len("followerfname\\\":\\\"")
            endIndex = pageString.find("\\\"", startIndex)
            searchIndex = endIndex
            fName = pageString[startIndex:endIndex].strip()
            startIndex = pageString.find("followerlname", searchIndex) + len("followerlname\\\":\\\"")
            endIndex = pageString.find("\\\"", startIndex)
            searchIndex = endIndex
            lName = pageString[startIndex:endIndex].strip()
        if name == fName + " " + lName:
            break   
        entrantIndex =  pageString.find("entrantid\\\":\\\"", endIndex)
        searchIndex = entrantIndex + len("entrantid\\\":\\\"")
    couplePlacementInfo = None

    data = pageString[pageString.find("partnershiporder"):pageString.find("Final")]
    cutNames = ["Final"]
    designations = re.findall("designation\":\".*?\"", data)
    index = len(designations) - 1
    while index >= 0:
        currDes = designations[index]
        currDes = currDes[currDes.find(":\"") + 2:currDes.rfind("\"")]
        cutNames.append(currDes)
        index -= 1
    orders = re.findall('partnershiporder.*?]', data)
    index = 0
    rank = {}
    placement = 1
    for order in orders:
        orders[index] = order[order.find("[") + 1:order.find("]")]
        index+=1

    cutNum = len(orders) - 1
    cutsChecked = 0
    couplePlacement = -1
    numCouples = len(orders[0].split(','))
    coupleCut = ''
    while cutNum >= 0:
        index = 0
        cut = orders[cutNum]
        idList = cut.split(',')
        while index < len(idList):
            if int(idList[index]) == entrantID:
                couplePlacement = placement
                coupleCut = cutNames[cutsChecked]
                couplePlacementInfo = [couplePlacement, numCouples, coupleCut]
            if int(idList[index]) not in rank:
                rank[int(idList[index])] = 1
                placement += 1         
            index += 1
        cutNum -= 1
        cutsChecked += 1

    print(titleName + " " + str(couplePlacementInfo[0]) + "/" +str(couplePlacementInfo[1]) + "(" +couplePlacementInfo[2] + ")" )
    return [titleName, couplePlacementInfo[0], couplePlacementInfo[1], couplePlacementInfo[2]]

        
def getDancerCompStats(cid, name, isLead=True, fileName=None):
    pageString = helper.getWebPage(getURL(cid))[0]
    if type(pageString) != str:
        print("Error getDancerCompStats(): " + getURL(cid)+ " failed to open")
        return None
    eventData = pageString[pageString.find("./results"):pageString.rfind("<!-- Footer -->")]
    allEvents = re.findall("eid=.*?</a>", eventData)
    compName = pageString[pageString.find("<h1>") + len("<h1>Results for "):pageString.find("</h1>")]
    file = None
    if fileName != None:
        file = open(fileName, "w")
        file.write(name + "'s Results at " + compName + '\n')
        file.write("Event Name, Placement, # of Couples, Cut\n")
    else:
        print(name + "'s Results at " + compName)
    for event in allEvents:
        eid = int(event[event.find("eid=") + len("eid="): event.find('\"')])
        placement = getDancerPlacement(cid, eid, name, isLead)
        if placement != None:
            if fileName == None:
                print(placement[0] + "| Place:" + str(placement[1]) +"/"+str(placement[2]) + "(" + placement[3] + ")")
            else:
                file.write(placement[0] + "," + str(placement[1]) +","+str(placement[2]) + ","+ placement[3] + "\n")
    if fileName != None:
        file.close()

if __name__ == '__main__':
    scrapeComp(113, "gamecock.txt")