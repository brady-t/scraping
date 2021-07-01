import requests
from bs4 import BeautifulSoup
import mysql.connector
import database
import re

entireList = []
URL = "https://www.indeed.com/cmp/Systems-Planning-and-Analysis,-Inc.-(spa)/reviews?fcountry=ALL&start=0"

while True:

    httpObject = requests.get(URL)
        
    # error checking

    if httpObject.status_code != 200:
        print("Failed to load, status code: ", httpObject.status_code)
    elif httpObject.status_code == 200:
        print("Successfully loaded site")

    soup = BeautifulSoup(httpObject.content, 'html.parser')

    # finding all ratings
    
    ratings = soup.find_all("button",class_= "css-1hmmasr-Text e1wnkr790")

    # set up MySQL 
    
    db = mysql.connector.connect(
            host="localhost", 
            user="root",
            passwd="root",
            database = "testdatabase"
            )

    mycursor = db.cursor()

    # find review-id
    # WIP - need review-id to update proper row with Helpful/Unhelpful votes
    ids = soup.find_all("div", attrs={"data-tn-entitytype" : "reviewId"}, class_="css-snxk27-Flex e37uo190")
    
    idList = []
      
    for id in ids:
       
       # query = "INSERT INTO IndeedReviews (ID) values (%s)"
       # value = (str(id['data-tn-entityid']))
        
        idList.append(id['data-tn-entityid'])
        entireList.append(id['data-tn-entityid'])

         
    # find info of reviews 

    info = soup.find_all("span",class_= "css-1i9d0vw-Text e1wnkr790", attrs={"itemprop" : "author"})
    indexList = 0

    for myInfo, myRating in zip(info, ratings):

        text = myInfo.text

        # status
        pattern1 = re.compile(r'\(((Current Employee)|(Former Employee))\)')
        status = (pattern1.search(text))
        startIndexStatusParenthesis = status.span()[0]
        endIndexStatusParenthesis = status.span()[1]
        employeeStatus = (text[startIndexStatusParenthesis:endIndexStatusParenthesis]).lstrip("(").rstrip(")")
        # print(employeeStatus)

        # title
        indexParenthesis = text.find("(")
        title = text[:startIndexStatusParenthesis]
        # print(title)
        
        # location
        listDashIndex = []
        for i in re.finditer('-',text):
            listDashIndex.append(i.span()[1])
        location = text[listDashIndex[0]:listDashIndex[1]]
        location = location.rstrip("-")
        location = location.strip()

        # date of publication
        date = (text[listDashIndex[1]:]).strip()

        # save to DB
        values = ("abcd1234")
        query = "INSERT INTO IndeedReviews (ID, Title, Status, Rating, Location, Date) values (%s,%s,%s,%s,%s,%s)"
        values = (idList[indexList] ,title, employeeStatus, myRating.text, location, date)
        indexList += 1
        mycursor.execute(query,values)
        db.commit()
        print("Successfully saved info, ratings to database")







    # helpful / unhelpful votes
    # votes = soup.find_all("div",class_ = "css-s0m1dl-Box eu4oa1w0")

    # # use parents to find general review block of html and then go deeper to find the 
    # # change ID to reviewID - ex:  data-tn-entityid="1eq62iglgu35m800" 
    # # data-tn-entityid is unique to each review 
    # for i in votes:
    #     print(i.text)
    #     # for j in i.parents:
    #     #     print(j)
    #     pattern = re.compile(r'\d')
    #     #pattern.search(i.text).group())

    # test = soup.select('div[data-tn-entityid]')
    # print("test len = ", len(test))

    # scrape next page of reviews if it exists
    link = soup.find("a",attrs={"data-tn-element" : "next-page", "data-tn-link" : "true"})
    if link == None or len(link) == 0:
        break
    else:
        URL = "https://www.indeed.com" + (link.get('href'))

# WIP - get rid of featured review because it's duplicated on each page 
# dup = []
# for x in entireList:
#     if entireList.count(x) > 1:
#         dup.append(x)
# print(dup)


