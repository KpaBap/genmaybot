#!/usr/bin/env bash
# This file can be called repeatedly from crontab to ensure the bot stays running 

BOTDIR=/path/to/bot/

PID=$(pgrep -f "python genmaybot.py")
if [ -z $PID ]; then
        echo "Bot not found running, starting..."
        cd $BOTDIR
        source venv/bin/activate
        python genmaybot.py & > /dev/null  2>&1
else
        echo "Bot already running."
fi
