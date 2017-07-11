from app import models, db, moonphase
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
    now = datetime.datetime.utcnow()
    today = datetime.datetime(now.year, now.month, now.day)

    morning = (today + datetime.timedelta(hours=6), 'Morning')
    day = (today + datetime.timedelta(hours=12), 'Day')
    evening = (today + datetime.timedelta(hours=18), 'Evening')
    night = (today + datetime.timedelta(hours=24), 'Night')
    tomorrow = (today + datetime.timedelta(hours=36), 'Tomorrow')

    print('now: %s utc' % now)
    print('today: %s utc' % today)
    print('morning: %s %s utc' % morning)
    print('day: %s %s utc' % day)
    print('night: %s %s utc' % night)
    print('tomorrow: %s %s utc' % tomorrow)

    local_hour = now.hour + 3
    if local_hour < 4:
        next1 = [morning, day, evening]
    elif local_hour < 10:
        next1 = [day, evening, tomorrow]
    elif local_hour < 16:
        next1 = [evening, night, tomorrow]
    elif local_hour < 22:
        tomorrow_morning = (today + datetime.timedelta(hours=30), 'Morning')
        next1 = [night, tomorrow_morning, tomorrow]
    else:
        tomorrow_morning = (today + datetime.timedelta(hours=30), 'Morning')
        tomorrow = (tomorrow[0], 'Day')
        tomorrow_evening = (today + datetime.timedelta(hours=42), 'Evening')
        next1 = [tomorrow_morning, tomorrow, tomorrow_evening]

        print('tomorrow_morning: %s %s' % tomorrow_morning)
        print('tomorrow_evening: %s %s' % tomorrow_evening)

    print(next1)

    ret = []

    response = requests.get(forecast_url)
    if response.status_code == 200:
        forecast = json.loads(response.text)
        for n in next1:
            timestamp = calendar.timegm(n[0].utctimetuple())
            item = next((x for x in forecast['list'] if x['dt'] == timestamp), None)
            if item:
                code = item['weather'][0]['id']
                if n[1] == 'Night' and code == 800:
                    icon = moonphase.moonphase(datetime.datetime.now())[0]
                else:
                    icon = get_icon(code)
                ret.append((n[1], int(item['main']['temp'] + 0.5), icon, item['weather'][0]['main']))
    return ret
