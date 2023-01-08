#! /usr/bin/python3

import logging
import sys

logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/usr/local/www/rover/')
from rover import app as application

application.secret_key = 'mars'
