#! /usr/bin/python3

import sys
import os

my_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, my_dir)

from rover import app as application
