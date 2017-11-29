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
    #print('😞'.encode('utf-8'))
    log.info('Bot token is %s' % app.config.get('BOT_TOKEN'))

    set_hook = requests.get(URL + 'setWebhook?url=')
    if not set_hook.ok:
        log.error("Can't remove hook: %s. Quit." % set_hook.text)
        exit(1)

    last_update_id = models.Data.query.filter_by(key='last_update_id').first()
    if last_update_id is None:
        last_update_id = models.Data(key='last_update_id', value=0)
    last_update_id_val = int(last_update_id.value)

    first_run = True
    tmo = MIN_TMO
    while True:
        res = requests.get('%sgetUpdates?offset=%s' % (URL, last_update_id_val))
        if res.ok:
            json = res.json()
            if not json['ok'] or not json['result']:
                tmo *= 1.5
            else:
                #log.info('%s' % json)
                updates = json['result']
                for message in updates:
                    if 'update_id' in message:
                        update_id = message['update_id']
                        if update_id > last_update_id_val:
                            last_update_id_val = update_id

                            if message and 'message' in message:
                                if not first_run:
                                    response = process_message(message['message'])
                                    if response.get('add') is None:
                                        requests.request('post', '%s%s' % (URL, response['method']), data=response)
                                    else:
                                        add = response.get('add')
                                        response['add'] = None
                                        requests.request('post', '%s%s' % (URL, response['method']), data=response)

                                        for add_msg in add:
                                            requests.request('post', '%s%s' % (URL, response['method']), data=add_msg)

                            if message and 'callback_query' in message:
                                message['callback_query']['message']['text'] = message['callback_query']['data']
                                response = process_message(message['callback_query']['message'])
                                requests.request('post', '%s%s' % (URL, response['method']), data=response)

                            last_update_id.value = str(last_update_id_val)
                            last_update_id.last_updated = datetime.datetime.now()
                            db.session.add(last_update_id)
                            db.session.commit()

                first_run = False
                tmo = MIN_TMO

        if tmo > MAX_TMO:
            tmo = MAX_TMO
        sleep(tmo)
except KeyboardInterrupt:
    signal_term_handler(signal.SIGTERM, None)
except Exception as e:
    logging.error('Start failed: %s' % e)
