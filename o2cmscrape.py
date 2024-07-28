import helper
import ConfigRequest
import datetime
import classes

#event= -> identifier for comp, heat= -> identifer for event

#Must be at the end of every url once you are passed results.o2cm.com. &bclr=#FFFFFF&tclr=#000000
rounds = ['Final', 'Semifinal', 'Quarterfinal', 'First Round']

def getURL(event = None, heat:str = ""):
    baseURL = "https://results.o2cm.com"
    urlEnd = "&bclr=#FFFFFF&tclr=#000000"
    if event == None:
        return baseURL
    else:
        baseURL += event #"/event3.asp?event=<eventtag>"
        if heat == "":
            baseURL += urlEnd
            return baseURL
        else:
            baseURL += "&heatid=" + heat + urlEnd
            return baseURL
def stringCodeToInt(code:str = ""):
    value = 0
    if code == "":
        return ""
    for c in code:
        if c >= '0' and c <= '9':
            value = value*10 + ord(c) - ord('0')
            continue
        else:
            value = value*1000 + ord(c)
    return value

def scrapeCompList():
    url = getURL()
    pageString = helper.getWebPage(url)[0]
    f = open("o2cmComps.csv", "w")
    beginIndex = 0
    endIndex = 0
    eventToCompNameDict = {}
    yearLocations = []
    f.write("target,cid,comp_name,date,city,state\n")#str(self.cid) + ',' + self.name + ',' + self.date.strftime("%x") + ',' + self.city + ',' + self.state
    while (beginIndex:= pageString.find('align=center', endIndex)) != -1:
        endIndex = pageString.find('</td>', beginIndex)
        yearLocations.append((beginIndex, pageString[beginIndex + len('align=center>'):endIndex]))
        beginIndex = endIndex
        
    beginIndex = 0
    endIndex = 0
    yearIndex = 0
    nextYearLocation = yearLocations[yearIndex][0]
    currYear = None
    while (beginIndex:= pageString.find('class=t1n', beginIndex)) != -1:
        #Get year
        if nextYearLocation < beginIndex:
            currYear = yearLocations[yearIndex][1]

        #Get month
        beginIndex += len('class=t1n><td>')
        endIndex = pageString.find('</td>', beginIndex)
        currMonthDay = pageString[beginIndex:endIndex]
        currDate = datetime.datetime(int(currYear), helper.monthAbrevToInt(currMonthDay[0:3]), int(currMonthDay[3:].strip()))
        beginIndex = pageString.find('event', endIndex)
        endIndex = pageString.find('&', beginIndex)
        eventTarget = pageString[beginIndex:endIndex] #find some way to turn this into valid int. some kind of hash?
        beginIndex = pageString.find('>', endIndex)
        beginIndex += 1 #Getting past > character
        endIndex = pageString.find('<', beginIndex)
        compName = pageString[beginIndex:endIndex]
        f.write(eventTarget + ',' + classes.Comp(5, compName, currDate, "", "").toString() + '\n') #compName + ' | ' + currDate

    f.close()

    return eventToCompNameDict

def scrapeCompResults(eventTarget:str, filename=None): 
    url = getURL(eventTarget)
    requestHeader = { "Accept": ConfigRequest.accept, "User-Agent": ConfigRequest.useragent}
    eventTag = eventTarget[eventTarget.find('event=') + len('event='):]
    payload = {'selDiv': '', 'selAge': '', 'selSkl': '', 'selSty': '', 'selEnt': '', 'submit': 'OK', 'event': eventTag}
    response = helper.getWebPage(url, requestHeader, payload)
    webPage = response[0]
    titleIndex = webPage.find('class=h4>') + len('class=h4>')
    compName = webPage[titleIndex:webPage.find('<', titleIndex)]
    pageFile = open("testing.txt", "w")
    pageFile.write(webPage)
    pageFile.close()
    
    
    divs = []
    ages = []
    skills = []
    styles = []
    #Generate divs, ages, skills, styles from page
    #Generate divs at this comp
    start = webPage.find('selDiv')
    stop = webPage.find('selAge')
    beginIndex = start
    while (beginIndex:=webPage.find('uidheat', beginIndex)) < stop:
        beginIndex = webPage.find('">', beginIndex) + 2
        divs.append(webPage[beginIndex:webPage.find('<', beginIndex)])
    #Generate ages at this comp
    start = stop
    stop = webPage.find('selSkl')
    beginIndex = start
    while (beginIndex:=webPage.find('uidheat', beginIndex)) < stop:
        beginIndex = webPage.find('">', beginIndex) + 2
        ages.append(webPage[beginIndex:webPage.find('<', beginIndex)])
    #Generate skills at this comp
    start = stop
    stop = webPage.find('selSty')
    beginIndex = start
    while (beginIndex:=webPage.find('uidheat', beginIndex)) < stop:
        beginIndex = webPage.find('">', beginIndex) + 2
        skills.append(webPage[beginIndex:webPage.find('<', beginIndex)])
    #Generate styles at this comp
    start = stop
    beginIndex = start
    while (beginIndex:=webPage.find('uidheat', beginIndex)) != -1:
        beginIndex = webPage.find('">', beginIndex) + 2
        styles.append(webPage[beginIndex:webPage.find('<', beginIndex)])
    
    beginIndex = 0
    file = None
    if filename == None:
        file = open(f"{eventTag}.csv", "w") #default file
    else:
        file = open(filename, "w")
    file.write(compName + '\n')
    while(beginIndex:= webPage.find('heatid=', beginIndex)) != -1:
        beginIndex += len('heatid=')
        heatid = stringCodeToInt(webPage[beginIndex:webPage.find('&', beginIndex)])
        beginIndex = webPage.find('target=_blank>', beginIndex)
        beginIndex += len('target=_blank>')
        eventName = webPage[beginIndex:webPage.find('<', beginIndex)]
        nextEventIndex = webPage.find('heatid=', beginIndex)
        entryBeginIndex = beginIndex
        endOfRound = webPage.find('<td>----</td>', beginIndex)
        currRound = 0
        entryList = []

        while True:
            entryBeginIndex = webPage.find('class=t2', entryBeginIndex)
            if entryBeginIndex == -1 or (entryBeginIndex > nextEventIndex and nextEventIndex != -1):
                break
            if entryBeginIndex > endOfRound:
                if currRound < len(rounds) - 1:
                    currRound += 1
                endOfRound = webPage.find('<td>----</td>', entryBeginIndex)
            entryNameBeginIndex = webPage.find(')', entryBeginIndex)
            placement = webPage[webPage.find('>', entryBeginIndex) + 1: entryNameBeginIndex]
            entryNameBeginIndex += 2 #Getting past ) and a space to slice couple num
            coupleNum = int(webPage[entryNameBeginIndex:webPage.find(' ', entryNameBeginIndex)])
            entryNameBeginIndex = webPage.find(' ', entryNameBeginIndex) + 1
            coupleNames = webPage[entryNameBeginIndex:webPage.find('<', entryNameBeginIndex)].split(' &amp; ') # (leadName, followName)
            if (dashIndex:= coupleNames[1].find(' -')) != -1:
                coupleNames[1] = coupleNames[1][:dashIndex]
            entryList.append(classes.Entry(coupleNum, coupleNames[0], coupleNames[1], placement, rounds[currRound], heatid))
            entryBeginIndex = entryNameBeginIndex

        heatInfo = [heatid] #eid:str, category: str, age: str, level: str, style: str, dances: str, entries: list, cid: str
        #search and store division
        eventName = eventName[1:] #cut out space in back
        for i in range(len(eventName)+1):        
            if eventName[0:len(eventName)-i] in divs:
                heatInfo.append(eventName[0:len(eventName)-i])
                eventName = eventName[len(eventName)-i:]
                break
        eventName = eventName.strip()
        #search and store age
        for i in range(len(eventName)+1):
            if eventName[0:len(eventName)-i] in ages:
                heatInfo.append(eventName[0:len(eventName)-i])
                eventName = eventName[len(eventName)-i:]
                break
        eventName = eventName.strip()
        #search and store skill
        for i in range(len(eventName)+1):
            if eventName[0:len(eventName)-i] in skills:
                heatInfo.append(eventName[0:len(eventName)-i])
                eventName = eventName[len(eventName)-i:]
                break
        eventName = eventName.strip()
        #search and store style
        for i in range(len(eventName)+1):
            if eventName[0:len(eventName)-i] in styles:
                heatInfo.append(eventName[0:len(eventName)-i])
                eventName = eventName[len(eventName)-i:]
                break
        eventName = eventName.strip()
        #store dances
        heatInfo.append(eventName)
        #store cid
        heatInfo.append(eventTag)
        file.write(classes.Event(heatInfo[0], heatInfo[1], heatInfo[2], heatInfo[3], heatInfo[4], heatInfo[5], entryList, heatInfo[6]).toString())
    file.close()
    return True


if __name__ == '__main__':
    #scrapeCompList()
    scrapeCompResults('/event3.asp?event=ksd24', 'kansascity.csv')
