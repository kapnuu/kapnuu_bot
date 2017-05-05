from app import app, openweathermap, cbr, models, db, nn_traffic
import calendar
import datetime
from flask import json, request, abort, send_from_directory
import logging
import random
import config
from os import path

log = logging.getLogger('app')


def dt(u): return datetime.datetime.fromtimestamp(u)


def ut(d): return calendar.timegm(d.timetuple())


@app.route('/')
def index():
    # log.info('HEROKU_APP_NAME is %s' % config.Config.HEROKU_APP_NAME)
    return 'It works'


@app.route('/favicon.ico')
def favicon():
    abort(404)


@app.route('/weather-ico/<ico>')
def weather_ico(ico):
    return send_from_directory(path.join(app.root_path, 'static/weather-ico'),
                               ico)


def send_reply(resp):
    if 'method' not in resp:
        resp['method'] = 'sendMessage'
    return app.response_class(
        response=json.dumps(resp),
        status=200,
        mimetype='application/json'
    )


@app.route('/hook', methods=['GET', 'POST'])
def process_request2():
    return process_request()


@app.route('/%s/hook' % config.Config.REQUEST_TOKEN, methods=['GET', 'POST'])
def process_request():
    try:
        data = request.json  # json.loads(request.data)
        log.info(data)
        if data:
            message = None
            if 'message' in data:
                message = data['message']
            elif 'edited_message' in request.json:
                message = data['edited_message']

            if message:
                chat_id = message['chat']['id']

                text = message['text'].lower()
                if text.startswith('/start') or text == '/help':
                    return start_f(chat_id, message["from"].get("first_name"), message["from"].get("id"))
                elif text == '/whoami':
                    return whoami_f(chat_id, message["from"].get("id"))
                elif text == '/huify':
                    return huify_f(chat_id, True, message["from"])
                elif text == '/unhuify':
                    return huify_f(chat_id, False, message["from"])
                elif text == '/weather':
                    return weather_f(chat_id)
                elif text == '/traffic':
                    return nn_traffic_f(chat_id)
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
                elif text == '/test':
                    return test_img_f(chat_id)
                else:
                    return send_reply({'chat_id': chat_id, 'text': 'You said: %s. WTF?' % message['text']})
            else:
                log.error('No `message` in request.json: %s' % request.data)
        else:
            log.error('request.json is None: %s' % request.data)
    except Exception as ex:
        log.error('Something went wrong: %s' % ex)
    abort(400)


@app.route('/start')
def start_f(chat_id=None, who=None, who_id=None):

    if not who and not who_id:
        log.info('User #%s %s', (who_id, who))

    responses = ['Hello, %s!',
                 'Hi there, %s.',
                 'Дратути, %s!',
                 'Превед %s!!1111адинaдин',
                 'Привет, %s!',
                 'Hi, %s!']  # , 'Ксюшенька-пампушенька, любищь тебя, дурочку']

    hi = random.choice(responses) % (who if who else 'Human')

    resp = '''%s
Sorry, I am not very useful bot, I'm just a my creator's helper: now he is learning how to develop telegram bots.

You can get info by sending these commands:

/help — this message
/weather — get current weather in Nizhniy Novgorod (other cities TBD)
/currency — get currency (use /currency/<i>ISO</i>) to RUR rate
/now — get current date and time in UTC
/whoami — get your personal settings

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
        ico = 'https://%s.herokuapp.com/weather-ico/%s.png' % (config.Config.HEROKU_APP_NAME,
                                                               weather['weather'][0]['icon'])
        t = weather['main']['temp']
        resp = '''<a href="%s"><b>%s</b>: %s</a>
%s%s°C %s
%s UTC''' % (ico, weather['name'], weather['weather'][0]['main'], '-' if t < 0 else '', t,
             weather['weather'][0]['description'].capitalize(), dt(weather['dt']).strftime('%a %b %d %H:%M %Y'))
    else:
        resp = 'WTF?'

    if chat_id:
        # return send_reply({'method': 'sendPhoto',
        #            'chat_id': chat_id,
        #            'caption': resp,
        #            'photo': ico})
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
    resp = '%s UTC' % datetime.datetime.now().strftime('%a %b %d %T.%f %Y')

    if chat_id:
        # if random.choice([0, 1]) == 0:
        #    return send_reply({'chat_id': chat_id, 'sticker': 'BQADAgADeAcAAlOx9wOjY2jpAAHq9DUC'})
        return send_reply({'chat_id': chat_id, 'text': resp})
    return '<h1>%s</h1>' % resp


@app.route('/traffic')
def nn_traffic_f(chat_id=None):
    resp = '''I don't know :('''
    res = nn_traffic.current_traffic()
    if res:
        resp = '''<b>Nizhniy Novgorod</b> traffic jams level is <b>%s</b> pt%s''' % (res[0], '' if res[0] == 1 else 's')
        if res[1]:
            resp += ': ' + res[1]
    if chat_id:
        return send_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<pre>%s</pre>' % resp


@app.route('/whoami')
def whoami_f(chat_id=None, who=None):
    who_id = who.get('id') if who else None
    who_name = who.get('first_name') if who else 'Human'
    greet = None
    huify = False
    user = models.BotUser.query.filter_by(telegram_id=who_id).first()
    if user:
        greet = user.greet
        huify = user.huify
        who_name = user.greet

    resp = '''Hello, %s!
    
This feature in development now.''' % who_name
    if huify:
        resp += '''

Use /unhuify to stop huifying your messages'''
    else:
        resp += '''

Use /huify to huify your messages'''
    if greet:
        resp += '''

You told me I can call you <b>%s</b>
Use /mynameis to change your personal greeting.''' % greet
    else:
        resp += '''

Use /mynameis if you want a personal greeting.'''

    if chat_id:
        return send_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<pre>%s</pre>' % resp


def huify_f(chat_id, huify, who):
    changed = True
    user = models.BotUser.query.filter_by(telegram_id=who.get('id')).first()
    if user:
        changed = user.huify != huify
        user.huify = huify
    else:
        user = models.BotUser(telegram_id=who.get('id'), huify=huify)

    if changed:
        resp = 'OK, %s, your messages will be %shuified now.' % (who.get('first_name'), '' if huify else 'un')
    else:
        resp = 'OK, %s, your messages are already %shuified.' % (who.get('first_name'), '' if huify else 'un')

    db.session.add(user)
    db.session.commit()
    return send_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})


def test_img_f(chat_id):
    ret = send_reply({'method': 'sendPhoto',
                      'chat_id': chat_id,
                      'caption': 'Test',
                      'photo': 'https://kapnuu-bot.herokuapp.com/weather-ico/03n.png'})
    # log.info(ret)
    return ret
