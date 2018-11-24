#!./.env/bin/python3
from flup.server.fcgi import WSGIServer
from backend.app import socketio

if __name__ == '__main__':
    WSGIServer(socketio, bindAddress="/tmp/seanonymous.sock", umask=0o007).run()
