import re
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

#The dates on the website have ranges and commas that need to be taken out to convert to date objects
def cleanDate(webDate): 
    formattedDate = re.sub("-.*?,", "", webDate)
    formattedDate = formattedDate.replace(',', '')
    data = formattedDate.split()
    finalDate = datetime.datetime(int(data[2]), monthToInt(data[0]), int(data[1]))
    return finalDate