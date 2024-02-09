#Will Miller
#Script to read Amateur competitor data from BallroomCompExpress and update database

#Where are we now: Can parse html fairly well. I can pull details about previous comps to store in db.
#Where are we going: Setup local db, figure out how to input competitions into db with their cid.

import re
import classes
import helper
import time


#TODO: Repurpose this function to add on to the file and expand it
def scrapeRecentComps(filename):
    #Open webpage and get string text
    pageString = helper.getWebPage(helper.getURL())
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
    recentCompFile = open(filename, "w")
    while index < len(compNames):
        compNames[index] = re.sub("<br>", "--", compNames[index])
        compNames[index] = re.sub("<.*?>", "", compNames[index])
        compInfo = compNames[index].split("--")
        recentCompFile.write(str(cidList[index]) + ' | ' + compInfo[0].strip() + ' | ' + helper.cleanDate(compInfo[1]).strftime("%x") + ' | ' + compInfo[2] +'\n')
        index += 1
    recentCompFile.close()

#Grabs all the events that match requirements and their eid's so we can traverse the website and check the results of each event
#args are strings that act as filters. If you don't want something like "Rookie-Vet" add "!Rookie-Vet" as an arg

def scrapeComp(cid, fileID, *argv):
    #open webpage
    text = helper.getWebPage(helper.getURL(cid))
    #Extact useful data
    eventData = text[text.find("./results"):text.rfind("<!-- Footer -->")]
    allEvents = re.findall("eid=.*?</a>", eventData)
    eidList = []
    compName = text[text.find("<h1>") + len("<h1>Results for "):text.find("</h1>")]
    filename = compName.replace(" ", "_") + fileID +".txt"
    
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
        if not flag:
            eid = int(allEvents[i][allEvents[i].find("eid=") + len("eid="): allEvents[i].find('\"')])
            eidList.append(eid) 
        i += 1
    file = open(filename, "w")
    print("Writing to File: " + filename)
    file.write(compName + '\n')
    remaining = len(eidList)
    print("Total Events: " + str(remaining))
    for eid in eidList:
        file.write(scrapeEvent(cid, eid).toString())
        remaining -=1
        print(str(eid) + " Captured (" + str(remaining) + " left)")
    file.close()

#There is a format assumption on the name of the event
# style1 and style2 are two words that makeup the name of the style EX: Int. Latin
#Amateur <age> <level> <style1> <style2> <dance> 
def getCompCid(compName):
    if type(compName) != str:
        print("Error getCompCid(): compName must be a str")
        return None
    if compName == "":
        print("Error getCompCid(): compName cannot be empty")
        return None
    file = open("recentComps.txt", "r")
    fileText = file.read()
    file.close()
    while fileText.find('\n') != -1:
        line = fileText[0 : fileText.find('\n')]
        fileText = fileText[fileText.find('\n') + 1:]
        data = line.split(" | ")
        if data[1] == compName:
            return int(data[0])
    #TODO: Add functionality that if the name cannot be found to update the comp file with new comps
    
def scrapeEvent(url, cid, eid):
    #open and get webpage
    pageString = helper.getWebPage(helper.getURL(cid, eid))
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
        entry = classes.Entry(couple[0], couple[1], results[key][0], results[key][1])
        coupleResults.append(entry)

    return classes.Event(eid, titleTokens[0], titleTokens[1], titleTokens[2], titleTokens[3] + ' ' + titleTokens[4], titleTokens[5],coupleResults, cid)

def getDancerPlacement(cid, eid, name, isLead=True):
    pageString = helper.getWebPage(helper.getURL(cid, eid))
    #Cutting excess information
    startIndex = pageString.find("Results for ") + len("Results for ")
    endIndex = pageString.find('<', startIndex)
    #Pulling event title
    titleName = pageString[startIndex:endIndex]

    names = helper.getCoupleNames(pageString)
    orders = helper.getCoupleOrder(pageString)
    index = 0
    if not isLead:
        index = 1
    for key in orders:
        if names[key][index] == name:
            return [titleName, orders[key][0], orders[key][1]]
    return None
        
def getDancerCompStats(cid, name, isLead=True): # This is bugged
    pageString = helper.getWebPage(helper.getURL(cid))
    eventData = pageString[pageString.find("./results"):pageString.rfind("<!-- Footer -->")]
    allEvents = re.findall("eid=.*?</a>", eventData)
    for event in allEvents:
        eid = int(event[event.find("eid=") + len("eid="): event.find('\"')])
        placement = getDancerPlacement(cid, eid, name, isLead)
        if placement != None:
            print(placement[0] + "| Place:" + str(placement[1]) + "(" + placement[2] + ")")
if __name__ == '__main__':
    
    #scrapeComp(113, "", "Amateur", "Adult")
    print(getDancerCompStats(67, "Jefferson Lindsay"))
