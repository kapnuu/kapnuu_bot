from app import models, db
import config
import requests
import json
import logging
import datetime
import calendar

log = logging.getLogger('app')

actuality = 30  # minutes

current_weather_url = 'http://api.openweathermap.org/data/2.5/weather?id=%s&appid=%s&units=metric' % \
                      (config.Config.OWM_CITYID, config.Config.OWM_APIKEY)

forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?id=%s&appid=%s&units=metric' % \
               (config.Config.OWM_CITYID, config.Config.OWM_APIKEY)


def verify_config():
    if config.Config.OWM_APIKEY is None:
        val = models.Data.query.filter_by(key='OWM_APIKEY').first()
        config.Config.OWM_APIKEY = val.value if val else None
        val = models.Data.query.filter_by(key='OWM_CITYID').first()
        config.Config.OWM_CITYID = val.value if val else None

        global current_weather_url
        current_weather_url = 'http://api.openweathermap.org/data/2.5/weather?id=%s&appid=%s&units=metric' % \
                              (config.Config.OWM_CITYID, config.Config.OWM_APIKEY)

        if not config.Config.OWM_APIKEY:
            with open('token.txt') as f:
                f.readline()
                f.readline()
                f.readline()
                config.Config.OWM_APIKEY = f.readline().strip()
                config.Config.OWM_CITYID = f.readline().strip()

        global forecast_url
        forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?id=%s&appid=%s&units=metric' % \
                       (config.Config.OWM_CITYID, config.Config.OWM_APIKEY)


def get_actual_value():
    weather = None
    verify_config()
    now = datetime.datetime.now()
    value = models.Data.query.filter_by(key='weather', param=str(config.Config.OWM_CITYID)).first()
    if value is None:
        response = requests.get(current_weather_url)
        if response.status_code == 200:
            log.info('current_weather: %s' % response.text)
            value = models.Data(key='weather', param=str(config.Config.OWM_CITYID), value=response.text,
                                last_updated=now)
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
            response = requests.get(current_weather_url)
            log.info('current_weather: %s' % response.text)
            weather = value.value = response.text
            value.last_updated = now
            db.session.add(value)
            db.session.commit()
            log.info('Updated `data` item: weather at %s' % now)
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


_clouds = u'\U00002601'
_fewClouds = u'\U000026C5'
_drizzle = u'\U0001F4A7'
_clear = u'\U00002600'
_rain = u'\U00002614'
# _extreme = u'\U0001F300'
_snow = u'\U00002744'
_thunderstorm = u'\U000026A1'
# _mist = u'\U0001F32B'
# _haze = u'\U0001F324'
_atmosphere = u'\U0001F301'
_hot = u'\U0001F300'


def get_icon(code):
    if code // 100 == 2 or (900 <= code <= 902) or code == 905:
        return _thunderstorm
    elif code // 100 == 3:
        return _drizzle
    elif code // 100 == 5:
        return _rain
    elif code // 100 == 6 or code == 903 or code == 906:
        return _snow
    elif code // 100 == 7:
        return _atmosphere
    elif code == 800:
        return _clear
    elif code == 801:
        return _fewClouds
    elif 802 <= code <= 804:
        return _clouds
    elif code == 904:
        return _hot


def get_forecast():
    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)

    morning = (today + datetime.timedelta(hours=9), 'Morning')
    day = (today + datetime.timedelta(hours=15), 'Day')
    evening = (today + datetime.timedelta(hours=21), 'Evening')
    night = (today + datetime.timedelta(hours=27), 'Night')
    tomorrow = (today + datetime.timedelta(hours=39), 'Tomorrow')

    if now.hour < 4:
        next1 = [morning, day, evening]
    elif now.hour < 10:
        next1 = [day, evening, tomorrow]
    elif now.hour < 16:
        next1 = [evening, night, tomorrow]
    elif now.hour < 22:
        next1 = [night, morning, tomorrow]
    else:
        tomorrow_morning = (today + datetime.timedelta(hours=33), 'Morning')
        tomorrow = (tomorrow[0], 'Day')
        tomorrow_evening = (today + datetime.timedelta(hours=45), 'Evening')
        next1 = [tomorrow_morning, tomorrow, tomorrow_evening]

    ret = []

    response = requests.get(forecast_url)
    if response.status_code == 200:
        forecast = json.loads(response.text)
        for n in next1:
            print(n)
            timestamp = calendar.timegm(n[0].utctimetuple()) - 3 * 60 * 60
            item = next((x for x in forecast['list'] if x['dt'] == timestamp), None)
            if item:
                icon = get_icon(item['weather'][0]['id'])
                ret.append((n[1], int(item['main']['temp'] + 0.5), icon, item['weather'][0]['main']))
                # print('%s %s %s°C' % (n[1], icon, int(item['main']['temp'] + 0.5)))
    return ret
