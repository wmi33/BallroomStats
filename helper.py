import re
import datetime
from urllib.request import urlopen

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
    if lowerMonth[0] == 'j':
        if lowerMonth[1] == 'a':
            return 1
        elif lowerMonth[2] == 'n':
            return 6
        else:
            return 7
    elif lowerMonth[0] == 'f':
        return 2
    elif lowerMonth[0] == 'm':
        if lowerMonth[2] == 'r':
            return 3
        else:
            return 5
    elif lowerMonth[0] == 'a':
        if lowerMonth[1] == 'p':
            return 4
        else:
            return 8
    elif lowerMonth[0] == 's':
        return 9
    elif lowerMonth[0] == 'o':
        return 10
    elif lowerMonth[0] == 'n':
        return 11
    else:
        return 12

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
        lFname = leaderFnames[index]
        lLname = leaderLnames[index]
        fFname = followerFnames[index]
        fLname = followerLnames[index]
        leaderName = lFname[lFname.find(':') + 3: lFname.rfind('\\\"')].strip() + " " + lLname[lLname.find(':') + 3: lLname.rfind('\\\"')].strip()
        followerName = fFname[fFname.find(':') + 3: fFname.rfind('\\\"')].strip() + " " + fLname[fLname.find(':') + 3: fLname.rfind('\\\"')].strip()
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
    