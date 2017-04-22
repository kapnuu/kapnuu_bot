from app import app, openweathermap, cbr
import calendar
import datetime
from flask import json, request, abort
import logging
import random
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
    data = request.json  # json.loads(request.data)
    if data:
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']

            log.info('id: %s' % message["from"].get("id"))

            text = message['text'].lower()
            if text.startswith('/start') or text == '/help':
                return start_f(chat_id, message["from"].get("first_name"), message["from"].get("id"))
            elif text == '/weather':
                return weather_f(chat_id)
            elif text.startswith('/currency'):
                iso = text[10:]
                if not iso:
                    iso = 'usd'
                return currency_f(iso, chat_id)
            elif text == 'замучить котов'\
                    or text == 'мучить котов'\
                    or text == 'torture cats':
                return send_reply({'chat_id': chat_id, 'text': 'КОТОВ МУЧИТЬ НЕЛЬЗЯ, СУЧКА!!'})
            elif text == '/now' or text == 'what time is it?':
                return now_f(chat_id)
            else:
                return send_reply({'chat_id': chat_id, 'text': 'You said: %s. WTF?' % message['text']})

    abort(400)


@app.route('/start')
def start_f(chat_id=None, who=None, who_id=None):

    if not who and not who_id:
        log.info('User #%s %s', (who_id, who))

    responses = ['Hello, %s!',
                 'Hi there, %s.',
                 'Дратути, %s!',
                 'Превед %s!!1111адинвдин',
                 'Привет, %s!',
                 'Hi, %s!']  # , 'Ксюшенька-пампушенька, любищь тебя, дурочку']

    hi = random.choice(responses) % (who if who else 'Human')

    resp = '''%s
Sorry, I am not very useful bot, I'm just a my creator's helper: now he is learning how to develop telegram bots.

You can get info by sending these commands:

/help — this message
/weather — get current weather in Nizhniy Novgorod (other cities TBD)
/currency — get currency (use /currency/<i>ISO</i>) to RUB rate
/now — get current date and time in UTC

Thanks, <i>kapnuu bot</i>

<b>P. S.</b> And do not try to torture cats. Never. NEVER!''' % hi

    if chat_id:
        return send_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<pre>%s</pre>' % resp


@app.route('/weather', methods=['GET'])
def weather_f(chat_id=None):
    resp = None

    weather = openweathermap.current_weather()
    if weather:
        t = weather['main']['temp']
        resp = '''<b>%s</b>: %s%s°C %s / %s
%s''' % (weather['name'], '-' if t < 0 else '', t, weather['weather'][0]['main'],
         weather['weather'][0]['description'], dt(weather['dt']).strftime('%a %b %d %H:%M %Y'))
    else:
        resp = 'WTF?'

    if chat_id:
        return send_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<h1>%s</h1>' % resp


@app.route('/currency/<iso>', methods=['GET'])
def currency_f(iso, chat_id=None):
    resp = None

    iso = iso.lower()
    if iso == 'rur':
        resp = '1 RUR is 1 RUR, dude!'
    else:
        rate = cbr.currency_rate(iso)
        if rate:
            resp = '1 %s = %s RUR' % (iso.upper(), rate)
        else:
            resp = "I don't know <i>%s</i>" % iso

    if chat_id:
        return send_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<h1>%s</h1>' % resp


@app.route('/now')
def now_f(chat_id=None):
    resp = datetime.datetime.now().strftime('%a %b %d %T.%f %Y')

    if chat_id:
        # if random.choice([0, 1]) == 0:
        #    return send_reply({'chat_id': chat_id, 'sticker': 'BQADAgADeAcAAlOx9wOjY2jpAAHq9DUC'})
        return send_reply({'chat_id': chat_id, 'text': resp})
    return '<h1>%s</h1>' % resp
