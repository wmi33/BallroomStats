#Will Miller
#Script to read Amateur competitor data from BallroomCompExpress and calculate placements

import re
import classes
import helper
import datetime

#creates a file with the list of recent competitions on the ballroomcompexpress website
#It will add on to the file. So it is possible to keep information on comps no longer on the recent comps list.
def scrapeRecentComps():
    filename = "recentcomps.csv"
    #Open webpage and get string text
    pageString = helper.getWebPage(helper.getURL())
    if type(pageString) != str:
        print("Error scrapeRecentComps(): " + helper.getURL()+ " failed to open")
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
                recentCompFile.write(str(cidList[index]) + ',' + compInfo[0].strip() + ',' + helper.cleanDate(compInfo[1]).strftime("%x") + ',' + cityState[0] + ',' + cityState[1] + '\n')
                listOfComps.append(classes.Comp(cidList[index], compInfo[0].strip(), helper.cleanDate(compInfo[1]), cityState[0], cityState[1]))
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
            recentCompFile.write(str(cidList[index]) + ',' + compInfo[0].strip() + ',' + helper.cleanDate(compInfo[1]).strftime("%x") + ',' + cityState[0] + ',' + cityState[1] +'\n')
            listOfComps.append(classes.Comp(cidList[index], compInfo[0].strip(), helper.cleanDate(compInfo[1]), cityState[0], cityState[1]))
            index += 1
        recentCompFile.close()
    return listOfComps

#Grabs all the events that match requirements and their eid's so we can traverse the website and check the results of each event
#args are strings that act as filters. If you don't want something like "Rookie-Vet" add "!Rookie-Vet" as an arg

def scrapeComp(cid, fileName, *argv):
    #open webpage
    pageString = helper.getWebPage(helper.getURL(cid))
    if type(pageString) != str:
        print("Error scrapeComp(): " + helper.getURL(cid)+ " failed to open")
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
        allEvents[i] = helper.getEventData(allEvents[i])
    
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
    pageString = helper.getWebPage(helper.getURL(cid, eid))
    if type(pageString) != str:
        print("Error scrapeEvent(): " + helper.getURL(cid, eid)+ " failed to open")
        return None
    #Cutting excess information
    startIndex = pageString.find("Results for ") + len("Results for ")
    endIndex = pageString.find('<', startIndex)
    #Pulling event title
    titleName = pageString[startIndex:endIndex]
    titleTokens = titleName.split()
    #Getting results
    results = helper.getCoupleOrder(pageString)
    eidToName = helper.getCoupleNames(pageString)
    coupleResults = []
    #Creating entries for event object
    for key in results.keys():
        couple = eidToName[key]
        entry = classes.Entry(key, couple[0], couple[1], results[key][0], results[key][1], eid)
        coupleResults.append(entry)
    return (coupleResults, titleTokens[-1]) #The last title token is the dances (list of classes.Entry, str)

#TODO: Add the partner as part of the information given about a person's results
def getDancerPlacement(cid, eid, name, isLead=True):
    pageString = helper.getWebPage(helper.getURL(cid, eid))
    if type(pageString) != str:
        print("Error getDancerPlacement(): " + helper.getURL(cid, eid)+ " failed to open")
        return None
    if isLead:
        dancerName = name.split()
        searchFirst = "leaderfname\\\":\\\"" + dancerName[0]
        searchLast = "leaderlname\\\":\\\"" + dancerName[1]
        if pageString.find(searchLast) ==  -1 or pageString.find(searchFirst) == -1:
            print("getDancerPlacement(): "+name+" not found for eid=" + str(eid))
            return None
    else:
        dancerName = name.split()
        searchFirst = "followerfname\\\":\\\"" + dancerName[0]
        searchLast = "followerlname\\\":\\\"" + dancerName[1]
        if pageString.find(searchLast) == -1 or pageString.find(searchFirst) == -1:
            print("getDancerPlacement(): "+name+" not found for eid=" + str(eid))
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
    couplePlacementInfo = helper.findPlacement(pageString, entrantID)
    print(titleName + " " + str(couplePlacementInfo[0]) + "/" +str(couplePlacementInfo[1]) + "(" +couplePlacementInfo[2] + ")" )
    return [titleName, couplePlacementInfo[0], couplePlacementInfo[1], couplePlacementInfo[2]]
        
def getDancerCompStats(cid, name, isLead=True, fileName=None):
    pageString = helper.getWebPage(helper.getURL(cid))
    if type(pageString) != str:
        print("Error getDancerCompStats(): " + helper.getURL(cid)+ " failed to open")
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
    print("hello")