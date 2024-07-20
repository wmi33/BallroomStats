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
    
def monthAbrevToInt(monthAbrev: str):
    lowerMonthAbrev = monthAbrev.lower()
    months = {'jan':1,
              'feb':2,
              'mar':3,
              'apr':4,
              'may':5,
              'jun':6,
              'jul':7,
              'aug':8,
              'sep':9,
              'oct':10,
              'nov':11,
              'dec':12,}
    try:
        result = months[lowerMonthAbrev]
        return result
    except:
        return None
    

    
    









    