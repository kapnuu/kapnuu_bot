import signal
import sys
from app import app, models, db
import logging
import requests
from time import sleep
from app.views import process_message
import datetime

URL = 'https://api.telegram.org/bot%s/' % app.config.get('BOT_TOKEN')
MIN_TMO = 2.0
MAX_TMO = 24.0


def signal_term_handler(signum, frame):
    print('SIGTERM received')
    sys.exit(1)

log = logging.getLogger('app')

signal.signal(signal.SIGTERM, signal_term_handler)

try:
    log.info('Bot token is %s' % app.config.get('BOT_TOKEN'))

    set_hook = requests.get(URL + 'setWebhook?url=')
    if not set_hook.ok:
        log.error("Can't remove hook: %s. Quit." % set_hook.text)
        exit(1)

    last_update_id = models.Data.query.filter_by(key='last_update_id').first()
    if last_update_id is None:
        last_update_id = models.Data(key='last_update_id', value=0)

    tmo = MIN_TMO
    while True:
        res = requests.get(URL + 'getUpdates')
        if res.ok:
            json = res.json()
            if not json['ok'] or not json['result']:
                tmo *= 1.5
            else:
                updates = json['result']
                for message in updates:
                    if 'update_id' in message:
                        update_id = message['update_id']
                        if update_id > int(last_update_id.value):
                            if message and 'message' in message:
                                response = process_message(message['message'])
                                requests.request('post', URL + response['method'], data=response)

                                last_update_id.value = str(update_id)
                                last_update_id.last_updated = datetime.datetime.now()
                                db.session.add(last_update_id)
                                db.session.commit()
                tmo = MIN_TMO

        if tmo > MAX_TMO:
            tmo = MAX_TMO
        sleep(tmo)
except KeyboardInterrupt:
    signal_term_handler(signal.SIGTERM, None)
except Exception as e:
    logging.error('Start failed: %s' % e)
