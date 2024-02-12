# BallroomStats
## Description
This project is designed to provide detailed statistics about Dancesport dancers using data provided by BallroomCompExpress.com
## How to Install and Run
You can download or clone the repository through this webpage. From there, I run this application using Python 3.11.4.
## How to Use
scrape.py includes 2 functions that can be run by making calls through it's main function or calling them in a Python interactive session.

### scrapeComp()
Given a competition ID, file name, and some keyword filters this function will create file with a summary report of all of the events that match the keywords. An example, my competitive team needs to look at our entire team's placements to see how we are progressing as a team. However, we only dance in Amateur Adult events and typically no higher than Novice. So, if I were lookin to print out the events my team competes in I would call scrapeComp() like this:

scrapeComp(121, results.csv, "Amateur", "Adult", "!Pre-Champ", "!Open", "!Championship")

This call says I am looking for events that have "Amateur" and "Adult" in the name but not "Pre-Champ", "Open", or "Championship". The exclamation point before the keyword is the equivalent of a NOT.

### getDancerCompStats()
Given a competition ID, competitor's full name, True/False if they are a lead or not, and a filename this function will look up and print out a competitor's placements at a competition. This one is pretty self explanatory in its use-case and how to use it. This function is very useful in my case when I am doing research on people I am competing against or checking my individual placements against others.

## Future for the project
1) Add functionality to lookup CID's with partial or whole competition name
2) Apply item 1 to the current functions to make them easier to use.
3) Rename functions to be more consistent with terminology (scrape = making calls to website, get = searching through a string)
4) Create a text-based UI in a separate module so the project can be used without any coding.
5) Function idea (dancerResume): Searches through all recent comps and prints out a competitor's placements in all of them. Provide some statistics about at what levels they are placing in
6) Function idea (versus): Given two names and a competition it will produce a comparison sheet showing how well one competitor placed over another in events they both competed in at a comp. 