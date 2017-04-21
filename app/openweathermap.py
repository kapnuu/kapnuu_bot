from app import models, db
import config
import requests
import json
import logging
import datetime

log = logging.getLogger('app')

actuality = 30  # minutes

url = 'http://api.openweathermap.org/data/2.5/weather?id=%s&appid=%s&units=metric' %\
          (config.OWM_CITYID, config.OWM_APIKEY)


def get_actual_value():
    weather = None
    now = datetime.datetime.now()
    value = models.Data.query.filter_by(key='weather', param=str(config.OWM_CITYID)).first()
    if value is None:
        response = requests.get(url)
        if response.status_code == 200:
            log.info('current_weather: %s' % response.text)
            value = models.Data(key='weather', param=str(config.OWM_CITYID), value=response.text, last_updated=now)
            db.session.add(value)
            db.session.commit()
            weather = value.value
        else:
            log.error(response.status_code)
        log.info('Created new `data` item: weather at %s' % now)
    else:
        diff = (now - value.last_updated)
        minutes = (diff.days * 86400 + diff.seconds) / 60
        if minutes > actuality:
            response = requests.get(url)
            log.info('current_weather1: %s' % response.text)
            weather = value.value = response.text
            value.last_updated = now
            db.session.add(value)
            db.session.commit()
            log.info('Updated `data` item: currency at %s' % now)
        else:
            weather = value.value

    return json.loads(weather)


def current_weather():
    weather = None
    try:
        weather = get_actual_value()
    except Exception as e:
        log.error('Failed to download data: %s' % e)
    return weather
