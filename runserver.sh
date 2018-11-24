#!/bin/bash
FLASK_SECRET=`cat .secret` .env/bin/python3 backend.fcgi
