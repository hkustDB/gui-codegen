import os
import logging

LOG_FORMAT = "%(asctime)s %(levelname)s : %(message)s"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

from aju_app import create_app
from aju_app import socketio

app = create_app(os.getenv('FLASK_CONFIG_NAME') or 'default')
# app.run(debug=True)
socketio.run(app, debug=True)
