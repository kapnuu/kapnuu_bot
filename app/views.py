from app import app, openweathermap, cbr
import calendar
import datetime
from flask import json, request, abort
import logging
# import config


@app.route('/')
def index():
    return 'It works'


@app.route('/favicon.ico')
def favicon():
    abort(404)


log = logging.getLogger('app')

# URL = 'https://api.telegram.org/bot%s/' % config.BOT_TOKEN
# HookURL = ''


def dt(u): return datetime.datetime.fromtimestamp(u)


def ut(d): return calendar.timegm(d.timetuple())


def send_reply(resp):
    if 'method' not in resp:
        resp['method'] = 'sendMessage'
    return app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )


@app.route('/hook', methods=['GET', 'POST'])
def process_request():
    log.info('process_request')
    abort(404)
    log.info('process_request: %s' % request)
    data = request.json  # json.loads(request.data)
    if data:
        if data['message']:
            message = data['message']
            chat_id = message['chat']['id']

            text = message['text']
            if text.startswith('/start'):
                return start_f(chat_id)
            elif text == '/help':
                pass
            elif text == '/weather':
                return weather_f(chat_id)
            elif text == '/currency':
                return currency_f('usd', chat_id)
            pass
    # abort(400)


@app.route('/start')
def start_f(chat_id=None):
    resp = 'Hello.'

    if chat_id:
        return send_reply({'chat_id': chat_id, 'text': resp})
    return '<h1>%s</h1>' % resp


@app.route('/weather', methods=['GET'])
def weather_f(chat_id=None):
    resp = None

    weather = openweathermap.current_weather()
    if weather:
        t = weather['main']['temp']
        resp = '%s%s&deg;C %s / %s' % ('-' if t < 0 else '', t, weather['weather'][0]['main'],
                                       weather['weather'][0]['description'])  # , dt(weather['dt']))
    else:
        resp = 'WTF?'

    if chat_id:
        return send_reply({'chat_id': chat_id, 'text': resp})
    return '<h1>%s</h1>' % resp


@app.route('/currency/<iso>', methods=['GET'])
def currency_f(iso, chat_id=None):
    resp = None

    rate = cbr.currency_rate(iso.lower())
    if rate:
        resp = '1 %s = %s RUR' % (iso.upper(), rate)
    else:
        resp = "I don't know <em>%s</em>" % iso

    if chat_id:
        return send_reply({'chat_id': chat_id, 'text': resp})
    return '<h1>%s</h1>' % resp
