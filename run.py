#!flask/bin/python
import os
import signal
import sys
from app import app
import logging
#import config
import requests

URL = 'https://api.telegram.org/bot%s/' % app.config.get('BOT_TOKEN')
HookURL = 'https://kapnuu-bot.herokuapp.com/%s/hook' % app.config.get('REQUEST_TOKEN')


def signal_term_handler(signum, frame):
    print('SIGTERM received')
    sys.exit(1)


signal.signal(signal.SIGTERM, signal_term_handler)
try:
    logging.info('Request token is %s' % app.config.get('REQUEST_TOKEN'))
    if app.config.get('BOT_TOKEN') and app.config.get('REQUEST_TOKEN'):
        get_hook = requests.get(URL + "getWebhookInfo")
        if get_hook.status_code != 200:
            logging.error("Can't get hook: %s. Quit." % get_hook.text)
            exit(1)
        if not get_hook.url or len(get_hook.url) == 0:
            set_hook = requests.get(URL + "setWebhook?url=%s" % HookURL)
            if set_hook.status_code != 200:
                logging.error("Can't set hook: %s. Quit." % set_hook.text)
                if set_hook.status_code != 429:  # "error_code":429,"description":"Too Many Requests: retry after 1"
                    exit(1)

    port = int(os.environ.get('PORT', 8881))
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
except KeyboardInterrupt:
    signal_term_handler(signal.SIGTERM, None)
