#!/usr/bin/python
from time import time
import re
import sys
import databaseconfig as cfg

try:
    import requests
    from bs4 import BeautifulSoup
    import mysql.connector
except ImportError as error:
    print("Missing module(s): request, bs4, or mysql.connector")
    sys.exit(1)
    
def setUpDB(myHost,myUser,myPassword,myDB):
    return mysql.connector.connect(
                host=myHost, 
                user=myUser,
                passwd=myPassword,
                database = myDB
                )

def saveToDB(database, query,values):
    mycursor = database.cursor()
    mycursor.execute(query,values)
    database.commit()

def findEmployeeStatus(text):
    statusPattern = re.compile(r'\(((Current Employee)|(Former Employee))\)')
    status = (statusPattern.search(text))
    startIndexStatusParenthesis = status.span()[0]
    endIndexStatusParenthesis = status.span()[1]
    return (text[startIndexStatusParenthesis:endIndexStatusParenthesis]).lstrip("(").rstrip(")")

def findTitle(text):
    indexParenthesis = text.find("(")
    titlePattern = re.compile(r'\(((Current Employee)|(Former Employee))\)')
    status = (titlePattern.search(text))
    startIndexStatusParenthesis = status.span()[0]
    return text[:startIndexStatusParenthesis]

def findLocation(text):
    listDashIndex = []
    for i in re.finditer('-',text):
        listDashIndex.append(i.span()[1])
    location = text[listDashIndex[0]:listDashIndex[1]]
    location = location.rstrip("-")
    return location.strip()

def findDate(text):
    listDashIndex = []
    for i in re.finditer('-',text):
        listDashIndex.append(i.span()[1])   
    return (text[listDashIndex[1]:]).strip()
    
def scrape(URL):   
    db = setUpDB(cfg.mysql["host"],cfg.mysql["user"],cfg.mysql["passwd"],cfg.mysql["database"])
    if db.is_connected():
        print("Connected to MySQL", db.get_server_info())
        print("Scraping . . . ")
        begin_time = time()
        
        while True:
            httpObject = requests.get(URL)
            if httpObject.status_code != 200:
                print("Failed to load, status code: ", httpObject.status_code)

            soup = BeautifulSoup(httpObject.content, 'html.parser')
            ratings = soup.find_all("button",class_= "css-1hmmasr-Text e1wnkr790")
            info = soup.find_all("span",class_= "css-1i9d0vw-Text e1wnkr790", attrs={"itemprop" : "author"})
            ids = soup.find_all("div", attrs={"data-tn-entitytype" : "reviewId"}, class_="css-snxk27-Flex e37uo190")
            
            idList = []
            for id in ids:
                idList.append(id['data-tn-entityid'])

            indexList = 0
            for myInfo, myRating in zip(info, ratings):
                text = myInfo.text
                employeeStatus = findEmployeeStatus(text)
                title = findTitle(text)
                location = findLocation(text)
                date = findDate(text)

                query = "INSERT INTO IndeedReviews (ID, Title, Status, Rating, Location, Date) values (%s,%s,%s,%s,%s,%s)"
                values = (idList[indexList] ,title, employeeStatus, myRating.text, location, date)
                indexList += 1
                saveToDB(db,query,values)
            
            # Scrape next page of reviews if it exists

            link = soup.find("a",attrs={"data-tn-element" : "next-page", "data-tn-link" : "true"})
            if link == None or len(link) == 0:
                end_time = time()
                print("Elapsed time: ", end_time - begin_time, "seconds")
                break
            else:
                URL = "https://www.indeed.com" + (link.get('href'))
        else:
            print("Failed to connect to DB")

if __name__ == "__main__":
    scrape("https://www.indeed.com/cmp/Systems-Planning-and-Analysis,-Inc.-(spa)/reviews?fcountry=ALL&start=0")
    
else:
    print("ScrapIndeed.py imported")
    