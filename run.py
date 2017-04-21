#!flask/bin/python
import os
import signal
import sys
from app import app
import logging
import config
import requests

URL = 'https://api.telegram.org/bot%s/' % config.Config.BOT_TOKEN
HookURL = 'https://kapnuu-bot.herokuapp.com/hook'


def signal_term_handler(signum, frame):
    print('SIGTERM received')
    sys.exit(1)


signal.signal(signal.SIGTERM, signal_term_handler)
try:
    if config.Config.BOT_TOKEN:
        set_hook = requests.get(URL + "setWebhook?url=%s" % HookURL)
        if set_hook.status_code != 200:
            logging.error("Can't set hook: %s. Quit." % set_hook.text)
            exit(1)

    port = int(os.environ.get('PORT', 8881))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
except KeyboardInterrupt:
    signal_term_handler(signal.SIGTERM, None)
