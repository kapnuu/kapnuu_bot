import requests
import re
import logging
import datetime
from app import models, db

traffic_descriptions = [
    'Traffic is moving freely',             # 0 'Дороги свободны',
    'Traffic is moving freely',             # 1 'Дороги свободны',
    'Traffic is moving fairly freely',      # 2 'Дороги почти свободны',
    'Areas of congestion',                  # 3 'Местами затруднения',
    'Areas of congestion',                  # 4 'Местами затруднения',
    'Traffic is heavy',                     # 5 'Движение плотное',
    'Traffic is backed up',                 # 6 'Движение затруднённое',
    'There are serious jams',               # 7 'Серьёзные пробки',
    'Jams extend for several km',           # 8 'Многокилометровые пробки',
    'Traffic is at a complete standstill',  # 9 'Город стоит',
    'Faster to walk',                       # 10 'Пешком быстрее',
]

log = logging.getLogger('app')

actuality = 30  # minutes


def get_traffic():
    idx = None
    r = requests.get('http://www.nn.ru')
    if r.status_code == 200:
        text = r.text
        g = re.search(r'([0-9]+)&nbsp;балл', text).groups()
        if len(g) > 0:
            idx = int(g[0])
    return idx


def get_actual_value():
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
            traffic = (traffic, traffic_descriptions[traffic])
            log.info('current_traffic: %s %s' % (traffic[0], traffic[1]))

    return traffic


def current_traffic():
    traffic = None
    try:
        traffic = get_actual_value()
    except Exception as e:
        log.error('Failed to download data: %s' % e)
    return traffic
