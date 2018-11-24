#!/bin/bash
if [ -e .secret ]
then
    FLASK_SECRET=`/bin/cat .secret` .env/bin/python3 backend.fcgi
else
    .env/bin/python3 backend.fcgi
fi


