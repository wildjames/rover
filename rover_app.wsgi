#! /usr/bin/python3

import logging
import sys

logging.basicConfig(filename="/home/rover/rover_app.log", level=logging.DEBUG)

sys.path.insert(0, '/usr/local/www/rover/')
from rover import app as application

application.secret_key = 'mars'
