#!/usr/bin/env python

import sys
import logging
logging.basicConfig(stream=sys.stderr)

app_path = "/var/www/markerminer"
if app_path not in sys.path:
    sys.path.insert(0,app_path)

from markerminer import create_app

application = create_app(configfile='site.cfg')
