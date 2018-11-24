from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send   #, #join_
import pymysql
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
ROOMS = {} #track active rooms


@app.route('/')
def hello_world():
    return 'Hello World!'

def messageReceived(methods=['Get', 'Post']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['Get', 'Post']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

def parseJSON(payload_json):
    data = json.loads(payload_json)
    cur.execute('SELECT ID FROM Client C WHERE ID = (%s)', data["clientid"])
    if(cur.rowcount == 0):
        id = data["clientid"]
        phoneNumber = data["forms"]["phone"]
        address = data["forms"]["Address"]
        firstName = data["forms"]["FirstName"]
        lastName = data["forms"]["LastName"]
        birthDate = data["forms"]["BirthDate"]
        email = data["forms"]["Email"]
        ssn = data["forms"]["SSN"]
        cur.execute('INSERT INTO Client(Id, CellPhone, Address, Email, SSN, FirstName, LastName, BirthDate, NextPayload) VALUES(%s, %s, %s,%s, %s, %s, %s, %s, "")', (id, phoneNumber, address, email, ssn, firstName, lastName, birthDate)) 
        conn.commit()    
    
if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', port= 3306, user='root', passwd='seanonymous', db='cse331')
    cur = conn.cursor()
    with open("../sample_ext_to_srv.json", "r") as f:
        data = f.read().replace('\n', '')
    parseJSON(data)
    #Run
    socketio.run(app, debug=True)
    
