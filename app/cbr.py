from app import models, db
from bs4 import BeautifulSoup
import requests
import logging
import datetime

log = logging.getLogger('app')

actuality = 2 * 60 * 60  # minutes

url = 'http://www.cbr.ru/scripts/XML_daily.asp'


def get_actual_value():
    now = datetime.datetime.now()
    value = models.Data.query.filter_by(key='currency').first()
    if value is None:
        response = requests.get(url)
        value = models.Data(key='currency', param=None, value=response.text, last_updated=now)
        db.session.add(value)
        db.session.commit()
        log.info('Created new `data` item: currency at %s' % now)
    else:
        diff = (now - value.last_updated)
        minutes = (diff.days * 86400 + diff.seconds) / 60
        if minutes > actuality:
            response = requests.get(url)
            value.value = response.text
            value.last_updated = now
        db.session.add(value)
        db.session.commit()
        log.info('Updated `data` item: currency at %s' % now)

    return value.value


def currency_rate(iso):
    cur = None
    try:
        data = get_actual_value()
        soup = BeautifulSoup(data, 'html.parser')
        all_currencies = soup.find_all('valute')
        cur = [cur for cur in all_currencies if cur.charcode.text.lower() == iso]
    except Exception as e:
        log.error('Failed to download data: %s' % e)

    if cur and len(cur) == 1:
        rate = (int(cur[0].nominal.text), float(cur[0].value.text.replace(',', '.')))
        log.info('currency_rate(%s) = %s' % (iso, rate))
        return rate
    else:
        log.info('currency_rate(%s) is unknown' % iso)
