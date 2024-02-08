import datetime
class Comp:
    def __init__(self, name: str, date: datetime.datetime, location: str): #Key in dictionary is CID
        self.name = name
        self.date = date
        self.location = location

class Event:
    def __init__(self, dances: str, style: str, level: str, age: str, entries: int, cid: int): #Key in dicionary is EID
        self.dances = dances
        self.style = style
        self.level = level
        self.age = age
        self.entries = entries
        self.cid = cid

class Entry:
    def __init__(self, eid: int, aidL: int, aidF: int, placement: int):
        self.eid = eid 
        self.aidF = aidF #Follow's Account ID
        self.aidL = aidL #Lead's Account ID
        self.placement = placement

class Dancer:
    def __init__(self, fname: str, lname: str, location: str): #Key in dictionary is AID
        self.fname = fname
        self.lname = lname
        self.location = location