#! /usr/bin/python3

import logging
import sys

logging.basicConfig(
    filename="/var/log/rover_wsgi.log",
    filemode='a',
    format="[%(asctime)s] [%(levelname)-8s]    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
sys.path.insert(0, '/usr/local/www/rover/')
from rover import app as application

application.secret_key = 'mars'
