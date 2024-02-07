#Will Miller
#Script to read data from BallroomCompExpress and update database

#Where are we now: Can parse html fairly well. I can pull details about previous comps to store in db.
#Where are we going: Setup local db, figure out how to input competitions into db with their cid.
from urllib.request import urlopen
import re
import classes
import datetime

def monthToInt(month):
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

def cleanDate(webDate): #The dates on the website have ranges and commas that need to be taken out to convert to date objects
    formattedDate = re.sub("-.*?,", "", webDate)
    formattedDate = formattedDate.replace(',', '')
    data = formattedDate.split()
    finalDate = datetime.datetime(int(data[2]), monthToInt(data[0]), int(data[1]))
    return finalDate

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
    compList = {}
    index = 0
    while index < len(compNames):
        compNames[index] = re.sub("<br>", "--", compNames[index])
        compNames[index] = re.sub("<.*?>", "", compNames[index])
        compInfo = compNames[index].split("--")
        compList[cidList[index]] = classes.Comp(compInfo[0].strip(), cleanDate(compInfo[1]), compInfo[2])
        index += 1
    recentCompFile = open(filename, "w")
    for cid in cidList:
        compString = str(cid) + ' | ' + compList[cid].name + ' | ' + compList[cid].date.strftime("%x") + ' | ' + compList[cid].location +'\n'
        recentCompFile.write(compString)
    recentCompFile.close()
    return compList

if __name__ == '__main__':
    baseURL = "https://www.ballroomcompexpress.com"

    #This is using an already loaded webpage to not constantly make requests to webserver
    #compList = scrapeRecentComps("url", "recentComps.txt")
    print(getWebPage("https://ballroomcompexpress.com/results.php?cid=121&eid=26"))
    
    #testFile = open("basePage", "w")
    #testFile.write(html)
    #testFile.close()
