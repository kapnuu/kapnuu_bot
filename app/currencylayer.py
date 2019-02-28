import logging
import requests

_URL = 'http://www.apilayer.net/api/live'

log = logging.getLogger('app')


def get_exchange_rate(api_key, from_currencies, to_currency):
    result = {}
    try:
        params = {
            'access_key': api_key,
            'format': 2,
            'currencies': ','.join(from_currencies)
        }
        r = requests.get(_URL, params=params)
        if r.status_code == 200:
            log.info('get_exchange_rate: %s', r.text)
            print('%s' % r.text)
            jrate = r.json()
            if jrate['success']:
                jquotes = jrate['quotes']
                if jrate['success'] and jquotes:
                    source = jrate['source'] or 'USD'
                    for from_cur in from_currencies:
                        usd = int(source == from_cur) or 1 / float(jquotes['{}{}'.format(source, from_cur)])
                        rate = usd * float(jquotes['{}{}'.format(source, to_currency)])
                        count = 1
                        while rate < 10:
                            count *= 10
                            rate *= 10
                        result[from_cur.lower()] = (count, rate)
            else:
                raise RuntimeError(jrate['error']['info'])
        else:
            log.warning('get_exchange_rate: %s', r.status_code)
    except Exception as e:
        log.error('Update currency rates failed: {0}'.format(e))
    return result
