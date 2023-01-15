#! /usr/bin/python3

import sys

sys.path.insert(0, '/usr/local/www/rover/')

from rover import app as application

application.secret_key = 'mars'
