from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send   #, #join_
import json
import os
from database import store_form_data, initDB

app = Flask(__name__)
app.config['SECRET_KEY'] #= os.environ["FLASK_SECRET"] or 'secret!'
socketio = SocketIO(app)
connected_clients = []



@app.route('/')
def hello_world():
    return 'Hello World!'

def messageReceived(methods=['Get', 'Post']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['Get', 'Post']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)


if __name__ == "__main__":
    initDB()
    with open("../sample_ext_to_srv.json") as f:
        clientid = 123
        data = json.load(f)
        store_form_data(data["forms"][0], clientid)
    socketio.run(app, debug=True)

