#!/bin/bash
if [ -e .secret ]
then
    FLASK_SECRET=`cat .secret` .env/bin/python3 backend.fcgi
else
    .env/bin/python3 backend.fcgi
fi


