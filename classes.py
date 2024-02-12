import datetime
class Comp:
    def __init__(self, cid: int, name: str, date: datetime.datetime, location: str, events: list): #Key in dictionary is CID
        self.name = name
        self.date = date
        self.location = location
        self.cid = cid
        self.events = events

    def toString(self):
        return str(self.cid) + ' | ' + self.name + ' | ' + self.date.strftime("%x") + ' | ' + self.location +'\n'
    
    def listEvents(self):
        compList = self.toString
        for ev in self.events:
            compList += "  " + ev.title() + '\n'
        return compList

class Event:
    #category, age, level, style, dances
    def __init__(self, eid:int, category: str, age: str, level: str, style: str, dances: str, entries: list, cid: int): #Key in dicionary is EID
        self.dances = dances
        self.category = category
        self.style = style
        self.level = level
        self.age = age
        self.entries = entries
        self.cid = cid
        self.eid = eid
    def title(self):
        return self.category + " " + self.age + " " + self.level + " " + self.style + " " + self.dances
    def toString(self):
        result = self.title() + '\n'
        result += "# of couples," + str(len(self.entries)) + '\n'
        result += "Placement, Lead Name, Follow Name, Cut\n"
        for ent in self.entries:
            result += ent.toString() + '\n'

        return result

class Entry:
    def __init__(self, lName: int, fName: int, placement: int, cut: str):
        self.fName = fName #Follow's Name
        self.lName = lName #Lead's Name
        self.placement = placement
        self.cut = cut
    def toString(self):
        return str(self.placement) + "," + self.lName + "," + self.fName  + "," + self.cut 

class Dancer:
    def __init__(self, fname: str, lname: str, location: str): #Key in dictionary is AID
        self.fname = fname
        self.lname = lname
        self.location = location