from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send   #, #join_
import pymysql

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


if __name__ == '__main__':
    conn = pymysql.connect(host='localhost', port= 3306, user='root', passwd='seanonymous', db='cse331')
    cur = conn.cursor()
    socketio.run(app, debug=True)
    
