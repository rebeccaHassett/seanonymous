#!/bin/bash
export SEANON_DIR=/home/seanonymous/seanonymous

if [ -e .secret ]
then
    read -r FLASK_SECRET < .secret
else
    FLASK_SECRET="secret!"
fi
if [ -e .user ]
then
    read -r SEANON_USER < .user
else
    SEANON_USER="admin"
fi
if [ -e .pass ]
then
    read -r SEANON_PASS < .pass
else
    SEANON_PASS="admin"
fi
    FLASK_SECRET="$FLASK_SECRET" SEANON_USER="$SEANON_USER" SEANON_PASS="$SEANON_PASS" .env/bin/python3 backend.fcgi
