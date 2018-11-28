#!./.env/bin/python3
from flup.server.fcgi import WSGIServer
from backend.app import socketio, app

if __name__ == '__main__':
    socketio.run(app, debug=False, use_reloader=False, host='127.0.0.1', port=5000)
