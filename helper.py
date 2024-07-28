from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


def getWebPage(url: str, headers=None, data=None) -> str:
    if headers == None:
        headers = {}
    if data == None:
        request = Request(url, data, headers)
    else:
        url_encoded_data = urlencode(data).encode('utf-8')
        request = Request(url, url_encoded_data, headers)
    try:
        response = urlopen(request)
    except HTTPError as error:
         print(error.status, error.reason)
    except URLError as error:
        print(error.reason)
    else:
        #http.client.HTTPResponse
        return (response.read().decode("utf-8"), response.getheaders())
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
    

    
    









    