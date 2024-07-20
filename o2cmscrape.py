import helper

#event= -> identifier for comp, heat= -> identifer for event

#Must be at the end of every url once you are passed results.o2cm.com. &bclr=#FFFFFF&tclr=#000000


def getURL(event:str = "", heat:str = ""):
    baseURL = "https://results.o2cm.com"
    urlEnd = "&bclr=#FFFFFF&tclr=#000000"
    if event == "":
        return baseURL
    else:
        baseURL += "/event3.asp?event=" + event
        if heat == "":
            baseURL += urlEnd
            return baseURL
        else:
            baseURL += "&heatid=" + heat + urlEnd
            return baseURL

def getCompList():
    url = getURL()
    pageString = helper.getWebPage(url)
    f = open("o2cm.txt", "w")
    f.write(pageString)
    f.close()
    beginIndex = 0
    endIndex = 0
    eventToCompNameDict = {}
    yearLocations = []
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
        currMonthDay = currMonthDay.replace(' ', '/')
        currDate = str(helper.monthAbrevToInt(currMonthDay[0:3]))+ currMonthDay[3:].strip() + '/' + currYear
        beginIndex = pageString.find('event=', endIndex) + len('event=\'')
        endIndex = pageString.find('&', beginIndex)
        event = pageString[beginIndex:endIndex]
        beginIndex = pageString.find('>', endIndex)
        beginIndex += 1 #Getting past > character
        endIndex = pageString.find('<', beginIndex)
        compName = pageString[beginIndex:endIndex]
        eventToCompNameDict[event] = compName + ' | ' + currDate

    return eventToCompNameDict

if __name__ == '__main__':
    f = open("o2cmComps.txt", "w")
    result = getCompList()
    for key in result.keys():
        f.write(key + ': ' + result[key] + '\n')
    f.close()
