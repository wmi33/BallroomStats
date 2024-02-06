#Will Miller
#Script to read data from BallroomCompExpress and update database

#Where are we now: Can parse html fairly well. I can pull details about previous comps to store in db.
#Where are we going: Setup local db, figure out how to input competitions into db with their cid.
from urllib.request import urlopen
import re

if __name__ == '__main__':
    baseURL = "https://www.ballroomcompexpress.com"
    #Actually opening the site
    #page = urlopen(baseURL) for testing leave this commented
    #pageString = webPage.read().decode("utf-8")

    #This is using an already loaded webpage to not constantly make requests to webserver
    page = open("basePage", "r")
    pageString = page.read()
    startIndex = pageString.find("<h2>Recent Comps</h2>") + len("<h2>Upcoming Comps</h2>")
    endIndex = pageString.find("</div></div>", startIndex)
    upcomingCompsList = pageString[startIndex:endIndex]
    compNames = re.findall("<span class=\"label\">.*?</div>", upcomingCompsList)
    index = 0
    while index < len(compNames):
        compNames[index] = re.sub("<br>", " -- ", compNames[index])
        compNames[index] = re.sub("<.*?>", "", compNames[index])
        index += 1
    print(compNames)
    page.close()
    #testFile = open("basePage", "w")
    #testFile.write(html)
    #testFile.close()
