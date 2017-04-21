#!flask/bin/python
import signal
import sys
from app import app
import logging
import config
import requests

URL = 'https://api.telegram.org/bot%s/' % config.BOT_TOKEN
HookURL = ''


def signal_term_handler(signum, frame):
    print('SIGTERM received')
    sys.exit(1)


signal.signal(signal.SIGTERM, signal_term_handler)
try:
    #  set_hook = requests.get(URL + "setWebhook?url=%s" % HookURL)
    #  if set_hook.status_code != 200:
    #      logging.error("Can't set hook: %s. Quit." % set_hook.text)
    #      exit(1)

    app.run(debug=True, port=8888)
except KeyboardInterrupt:
    signal_term_handler(signal.SIGTERM, None)
