# Snoonet #bicycling Bot
A python bot running on snoonet's #bicycling channel.

## Requirements
* python3
* [pip](https://pip.pypa.io/en/stable/installing/)
* [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)

## Setup
The following instructions have been provided to setup, run and develop this bot. 

### 1.) Checkout the code & setup your genmaybot.cfg
`$ git clone -b cycling git@github.com:KpaBap/genmaybot.git bicyclingbot`
This will checkout the `cycling` branch of this project into the folder bicyclingbot.

Inside this folder the bot codebase you will find a `genmaybot.cfg.example`, make a copy of it and name it `genmaybot.cfg`. You can edit the various settings in this file to configure your bot.

`$ cd bicyclingbot`
`$ cp genmaybot.cfg.example genmaybot.cfg`

### 2.) virtualenv
One of the following steps needs to be picked depending on wether or not your `python` version is linked to 2.x or 3.x.
`$ python --version`
If this returns 3.x then issue the following command (be sure you're in your bicyclingbot folder):
`$ virtualenv venv`
If this returns 2.x then issue then you'll need to find the path to your python3 executable and specifying it in virtualenv with the -p parameter.
`$ which python3`
This may output something like `/usr/local/bin/python3`, you'll need this for the following command:
`$ virtualenv -p /usr/local/bin/python3 venv`

This will setup your virtual environment for python and pip requirements, now you're ready to activate it by: 
`$ source venv/bin/activate`
You'll now see a `(venv)` in front of all your command prompts, if you ever need to drop out of this virtual environment, type `deactivate`.

### 3.) Install requirments with pip
`(venv) $ pip install -r requirements.txt`
This will install all the python requirments to make your bot work.

### 4.) Starting your bot
`(venv) $ python genmaybot.py`

## TL;DR
1. Checkout code
2. Setup genmay.conf
3. `$ virtualenv venv`
  Or if python is defaulted to python2.x; `$ virtualenv -p /path/to/your/pythong3 venv`
4. `$ source venv/bin/activate`
5. `(venv) $ pip install -r requirements.txt`
6. `(venv) $ python genmaybot.py`