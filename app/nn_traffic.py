import requests
import re
import logging
import datetime
from app import models, db

traffic_descriptions = [
    'Дороги свободны',
    'Дороги почти свободны',
    'Местами затруднения',
    'Местами затруднения',
    'Движение плотное',
    'Движение затруднённое',
    'Серьёзные пробки',
    'Многокилометровые пробки',
    'Город стоит',
    'Пешком быстрее',
]

log = logging.getLogger('app')

actuality = 30  # minutes


def get_traffic():
    idx = None
    r = requests.get('http://m.nn.ru')
    if r.status_code == 200:
        text = r.text
        g = re.search(r'([0-9]+)&nbsp;балл', text).groups()
        if len(g) > 0:
            idx = int(g[0])
    return idx


def get_actual_value():
    traffic = None
    now = datetime.datetime.now()
    value = models.Data.query.filter_by(key='traffic').first()
    if value is None:
        traffic = get_traffic()
        if traffic:
            value = models.Data(key='traffic', value=str(traffic), last_updated=now)
            db.session.add(value)
            db.session.commit()
            log.info('Created new `data` item: traffic at %s' % now)
        else:
            log.error('Failed to get current traffic jams level')
    else:
        diff = (now - value.last_updated)
        minutes = (diff.days * 86400 + diff.seconds) / 60
        if minutes > actuality:
            traffic = get_traffic()
            value.value = str(traffic)
            value.last_updated = now
            db.session.add(value)
            db.session.commit()
            log.info('Updated `data` item: traffic at %s' % now)
        else:
            traffic = int(value.value)

    if traffic:
        if 0 < traffic <= len(traffic_descriptions):
            traffic = (traffic, traffic_descriptions[traffic - 1])
            log.info('current_traffic: %s %s' % (traffic[0], traffic[1]))

    return traffic


def current_traffic():
    traffic = None
    try:
        traffic = get_actual_value()
    except Exception as e:
        log.error('Failed to download data: %s' % e)
    return traffic
