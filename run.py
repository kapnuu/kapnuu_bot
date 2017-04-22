#!flask/bin/python
import os
import signal
import sys
from app import app
import logging
#import config
import requests
import json

URL = 'https://api.telegram.org/bot%s/' % app.config.get('BOT_TOKEN')
HookURL = 'https://kapnuu-bot.herokuapp.com/%s/hook' % app.config.get('REQUEST_TOKEN')


def signal_term_handler(signum, frame):
    print('SIGTERM received')
    sys.exit(1)

log = logging.getLogger('app')

signal.signal(signal.SIGTERM, signal_term_handler)
try:
    log.info('Request token is %s' % app.config.get('REQUEST_TOKEN'))
    log.info('Bot token is %s' % app.config.get('BOT_TOKEN'))
    if app.config.get('BOT_TOKEN') is not None and app.config.get('REQUEST_TOKEN'):
        log.info('Getting webhook')
        get_hook = requests.get(URL + "getWebhookInfo")
        if get_hook.status_code != 200:
            log.error("Can't get hook: %s. Quit." % get_hook.text)
            exit(1)
        hook = json.loads(get_hook.text)
        if not hook['result']['url']:
            log.info('Setting webhook')
            set_hook = requests.get(URL + "setWebhook?url=%s" % HookURL)
            if set_hook.status_code != 200:
                log.error("Can't set hook: %s. Quit." % set_hook.text)
                if set_hook.status_code != 429:  # "error_code":429,"description":"Too Many Requests: retry after 1"
                    exit(1)
        else:
            log.info('Hook is set to %s' % hook['result']['url'])

    port = int(os.environ.get('PORT', 8881))
    log.info('Starting server at port %s' % port)
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=port)
except KeyboardInterrupt:
    signal_term_handler(signal.SIGTERM, None)
except Exception:
    logging.error('Start failed')
