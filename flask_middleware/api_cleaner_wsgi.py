#! /usr/bin/python3
import logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="/home/rover/rover/log/rover_flask.log",
    filemode="a",
    format="[%(asctime)s] %(levelname)-8s    %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

import sys
import os
from werkzeug.middleware.proxy_fix import ProxyFix

my_dir = os.path.dirname(os.path.realpath(__file__))
print(f"WSGI startup; inserting my_dir to path: {my_dir}")
sys.path.insert(0, my_dir)

from api_cleaner import app as application


application.wsgi_app = ProxyFix(
    application.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
