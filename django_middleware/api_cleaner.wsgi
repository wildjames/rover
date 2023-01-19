#! /usr/bin/python3

import sys
import os

my_dir = os.path.dirname(os.path.realpath(__file__))
print(f"WSGI startup; inserting my_dir to path: {my_dir}")
sys.path.insert(0, my_dir)

from api_cleaner import app as application

import logging
logging.basicConfig(stream=sys.stderr)
