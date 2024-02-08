#Will Miller
#Script to read Amateur competitor data from BallroomCompExpress and update database

#Where are we now: Can parse html fairly well. I can pull details about previous comps to store in db.
#Where are we going: Setup local db, figure out how to input competitions into db with their cid.
from urllib.request import urlopen
import re
import classes
import helper

def getWebPage(url):
    try:
        response = urlopen(url)
    except Exception as ex:
        return ex
    else:
        body = response.read().decode("utf-8")
    finally:
        if response is not None:
            response.close()
    return body

def scrapeRecentComps(url, filename):
    print(url)
    #Open webpage and get string text
    page = open("basePage", "r")
    pageString = page.read()
    page.close()
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

def scrapeComp(url, cid, filename, *argv):
    #open webpage
    file = open("compPage", "r")
    text = file.read()
    file.close()
    eventData = text[text.find("./results"):text.rfind("<!-- Footer -->")]
    allEvents = re.findall("eid=.*?</a>", eventData)
    eidList = []
    
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
    for eid in eidList:
        file.write(scrapeEvent(url, cid, eid).toString())
    file.close()

#Used by scrapeEvent() to get dictionary of entrantID's with corresponding lead and follow names
def getCoupleNames(pageString):
    coupleData = pageString[pageString.find("var dancers = "):pageString.rfind("followeraffiliation")]
    eidDict = {}
    index = 0
    eidValues = re.findall(r'entrantid.*?,', coupleData)
    leaderFnames = re.findall(r'leaderfname.*?,', coupleData)
    leaderLnames = re.findall(r'leaderlname.*?,', coupleData)
    followerFnames = re.findall(r'followerfname.*?,', coupleData)
    followerLnames = re.findall(r'followerlname.*?,', coupleData)
    for eid in eidValues:
        intEid = int(eid[eid.find(':') + 3: eid.rfind('\\\"')])
        lFname = leaderFnames[index]
        lLname = leaderLnames[index]
        fFname = followerFnames[index]
        fLname = followerLnames[index]
        leaderName = lFname[lFname.find(':') + 3: lFname.rfind('\\\"')] + " " + lLname[lLname.find(':') + 3: lLname.rfind('\\\"')]
        followerName = fFname[fFname.find(':') + 3: fFname.rfind('\\\"')] + " " + fLname[fLname.find(':') + 3: fLname.rfind('\\\"')]
        eidDict[intEid] = [leaderName, followerName]
        index += 1
    return eidDict
#Used by scapeEvent() to get dictionary of entrantID: [placement, cut]
def getCoupleOrder(pageString):
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
    #Still need to convert from entrantID to names
    return rank

#There is a format assumption on the name of the event
# style1 and style2 are two words that makeup the name of the style EX: Int. Latin
#Amateur <age> <level> <style1> <style2> <dance> 
def scrapeEvent(url, cid, eid):
    #open and get webpage
    pageString = getWebPage(url + "/results.php?cid=" + str(cid) + "&eid=" + str(eid))
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
        entry = classes.Entry(couple[0], couple[1], results[key][0], results[key][1])
        coupleResults.append(entry)

    return classes.Event(eid, titleTokens[0], titleTokens[1], titleTokens[2], titleTokens[3] + ' ' + titleTokens[4], titleTokens[5],coupleResults, cid)

if __name__ == '__main__':
    baseURL = "https://ballroomcompexpress.com"

    #This is using an already loaded webpage to not constantly make requests to webserver
    #compList = scrapeRecentComps("url", "recentComps.txt")
    #scrapeRecentComps("url", "recentComps.txt")
    #print(scrapeEvent(baseURL, 67, 174).toString())
    scrapeComp(baseURL,103, "comp_results.txt", "Amateur", "Adult", "Silver", "!International")
