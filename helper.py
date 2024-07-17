import re
import datetime
from urllib.request import urlopen

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

def getWebPage(url: str):
    try:
        response = urlopen(url)
    except Exception as ex:
        return ex
    else:
        body = response.read().decode("utf-8")
    return body
def monthToInt(month: str):
    lowerMonth = month.lower()
    months = {'january':1,
              'february':2,
              'march':3,
              'april':4,
              'may':5,
              'june':6,
              'july':7,
              'august':8,
              'september':9,
              'october':10,
              'november':11,
              'december':12,}
    if lowerMonth in months.keys():
        return months[lowerMonth]
    else:
        return -1
    
#test function to work with div data which will help reimplement scrapeEvent
#><div class="event-entry category3 age5 level15 style5 special1"><a href="./results.php?cid=115&eid=6780">
def getEventData(eventEntryString: str):
    if isinstance(eventEntryString, str) == False:
        print("getDances() paramaeter must be a string with the event name. EX: \"Amateur Adult Silver W/T/F")
        return None
    values = eventEntryString.split()
    return [category[int(values[1][len("category"):])],  age[int(values[2][len("age"):])], level[int(values[3][len("level"):])], style[int(values[4][len("style"):])]]
    
    

#The dates on the website have ranges and commas that need to be taken out to convert to date objects
def cleanDate(webDate: str): 
    formattedDate = re.sub("-.*?,", "", webDate)
    formattedDate = formattedDate.replace(',', '')
    data = formattedDate.split()
    finalDate = datetime.datetime(int(data[2]), monthToInt(data[0]), int(data[1]))
    return finalDate

#Used by scrapeEvent() to get dictionary of entrantID's with corresponding lead and follow names
def getCoupleNames(pageString: str):
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
        leaderName = None
        followerName = None
        try:
            lFname = leaderFnames[index]
            lLname = leaderLnames[index]
            leaderName += lFname[lFname.find(':') + 3: lFname.rfind('\\\"')].strip() + " " + lLname[lLname.find(':') + 3: lLname.rfind('\\\"')].strip()
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


#Used by getDancerPlacement to locate a specific placement. We don't need the whole list of placements
def findPlacement(pageString: str, entrantID: int):
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
                return [couplePlacement, numCouples, coupleCut]
            if int(idList[index]) not in rank:
                rank[int(idList[index])] = 1
                placement += 1
                
            index += 1
        cutNum -= 1
        cutsChecked += 1
    return None
def getURL(cid=None, eid=None):
    baseURL = "http://ballroomcompexpress.com"
    if cid == None:
        return baseURL
    elif(eid == None):
        return baseURL + "/results.php?cid=" + str(cid)
    else:
        return baseURL + "/results.php?cid=" + str(cid) + "&eid=" + str(eid)
    