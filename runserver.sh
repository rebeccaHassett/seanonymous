#!/bin/bash
export SEANON_DIR=/home/seanonymous/seanonymous
if [ -e .secret ]
then
    FLASK_SECRET=`/bin/cat .secret` .env/bin/python3 backend.fcgi
else
    .env/bin/python3 backend.fcgi
fi


