from app import app, openweathermap, cbr, models, db, nn_traffic, huificator, transcription, wordify, wiki_calendar, yandexgeo, emoji, currencylayer
import calendar
import datetime
from flask import json, request, abort, send_from_directory, render_template
import logging
import random
import config
from os import path
import requests

log = logging.getLogger('app')

# TODO use user timezone
tz_offset = 3 * 60 * 60 - int(app.config.get('BOT_TZ_OFFSET'))

nevelny = {}
BLET = ['CAADAgADowAD12sEFoKFW18ZTHA7Ag',
        'CAADAgADLwAD12sEFj-pk35Cn903Ag',
        'CAADAgADLgADa-HIEz-pZ80pPFhKAg',
        'CAADAgADiAAD12sEFnq1CqqkApnIAg']


URL = 'https://api.telegram.org/bot%s/' % app.config.get('BOT_TOKEN')


def dt(u):
    return datetime.datetime.fromtimestamp(u)


def ut(d):
    return calendar.timegm(d.timetuple())


@app.route('/')
def index():
    return 'It works'


@app.route('/favicon.ico')
def favicon():
    abort(404)


@app.route('/weather/ico/<ico>')
def weather_ico(ico):
    return send_from_directory(path.join(app.root_path, 'static/weather-ico'), ico)


@app.route('/traffic/ico/<ico>')
def traffic_ico(ico):
    return send_from_directory(path.join(app.root_path, 'static/traffic-ico'), ico)


def process_reply(resp):
    if 'method' not in resp:
        resp['method'] = 'sendMessage'
    return resp


@app.route('/%s/hook' % config.Config.REQUEST_TOKEN, methods=['GET', 'POST'])
def process_request():
    try:
        data = request.json
        #log.info(request.data)
        print('%s' % json.dumps(data))
        #  log.info(request.headers)
        if data:
            message = None
            if 'message' in data:
                message = data['message']
            elif 'edited_message' in data:
                message = data['edited_message']
            elif 'callback_query' in data:
                message = data['callback_query']['message']
                message['text'] = data['callback_query']['data']
                message['from'] = data['callback_query']['from']

            if message:
                if 'sticker' in message:
                    message['text'] = message['sticker']['emoji']
                    #print('%s' % json.dumps(data))
                elif 'document' in message:
                    message['text'] = 'TODO: send WTF response'
                elif 'new_chat_member' in message:
                    member = message['new_chat_member']['first_name']
                    message['text'] = f'Who is {member}?'
                response = process_message(message)
                if response:
                    return app.response_class(
                        response=json.dumps(response),
                        status=200,
                        mimetype='application/json'
                    )
            else:
                log.error('No `message` in request.json: %s' % request.data)
        else:
            log.error('request.json is None: %s' % request.data)
    except Exception as ex:
        log.error('Something went wrong: %s' % ex)
    abort(400)


@app.route('/start')
def start_f(chat_id=None, who=None, args=None, cmd=None):
    greet = None
    if who is not None:
        t_id = who.get('id')
        first_name = who.get('first_name')
        username = who.get('username')
        last_name = who.get('last_name')

        greet = name = first_name
        if username:
            name = '%s %s' % (name, username)
        if last_name:
            name = '%s %s' % (name, last_name)

        log.info('User #%s %s' % (t_id, name))

        user = models.BotUser.query.filter_by(telegram_id=t_id).first()
        if user is None:
            user = models.BotUser(telegram_id=t_id, name=name, huify=False, owm_city=config.Config.OWM_CITYID)
            db.session.add(user)
            db.session.commit()
        elif user.name is None:
            user.name = name
            db.session.commit()

        if user.greet:
            greet = user.greet

    responses = ['Hello, %s!',
                 'Hi there, %s.',
                 # 'Дратути, %s!',
                 # 'Привет, %s!',
                 'Hi, %s!']  # , 'Ксюшенька-пампушенька, любищь тебя, дурочку']

    hi = random.choice(responses) % (greet if greet else 'Human')

    resp = '''%s
You can get info by sending these commands:

/help — this message
/weather — get current weather in Nizhniy Novgorod (other cities TBD)
/currency — get currency (use /currency <i>ISO</i>) to RUR rate
/now — get current date and time in UTC/Unix timestamp
/whoami — get your personal settings
/traffic — traffic jams in Nizhniy Novgorod

Thanks, <i>kapnuu bot</i>

<b>P. S.</b> And do not try to <b>torture cats</b>. Never. NEVER!''' % hi

    if chat_id:
        return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<pre>%s</pre>' % resp


@app.route('/weather', methods=['GET'])
def weather_f(chat_id=None, who=None, args=None, cmd=None):
    weather = openweathermap.current_weather()
    if weather:
        log.info(weather)

        if app.config.get('HEROKU_APP_NAME'):
            base_url = 'https://%s.herokuapp.com/' % app.config.get('HEROKU_APP_NAME')
        else:
            base_url = '/'

        ico = 'weather/ico/%s.png' % weather['weather'][0]['icon']

        t = weather['main']['temp']
        t = '%.0f°C' % t  # '%s%s°C' % ('-' if t < 0 else '', t)

        city = weather['name']
        main = weather['weather'][0]['main']
        description = weather['weather'][0]['description'].capitalize()
        timestamp = dt(weather['dt'] + tz_offset).strftime('%a %b %d %H:%M %Y')

        wind = 'Wind'
        if 'deg' in weather['wind']:
            deg = weather['wind']['deg']

            if deg >= 338 or deg <= 22:
                wind = 'Northern'
            elif deg <= 67:
                wind = 'North-Eastern'
            elif deg <= 112:
                wind = 'Eastern'
            elif deg <= 157:
                wind = 'South-Eastern'
            elif deg <= 202:
                wind = 'Southern'
            elif deg <= 247:
                wind = 'South-Western'
            elif deg <= 292:
                wind = 'Western'
            elif deg <= 337:
                wind = 'North-Western'

            wind += ' wind,'

        sunrise = weather['sys']['sunrise'] + tz_offset
        sunset = weather['sys']['sunset'] + tz_offset
        day_d = sunset - sunrise
        seconds = day_d % 60
        minutes = int((day_d - seconds) / 60 + seconds / 60) % 60
        hours = (day_d - minutes * 60) // 60 // 60

        details = '%s %s&nbsp;mph. Humidity %s&nbsp;%%. Day duration is&nbsp;%s:%s: from&nbsp;%s to&nbsp;%s' % \
                  (wind, weather['wind']['speed'], weather['main']['humidity'], hours, str(minutes).zfill(2),
                   dt(sunrise).strftime('%H:%M'), dt(sunset).strftime('%H:%M'))

        if chat_id:
            res = '''<b>%s</b>: <a href="%sweather?%s">%s, %s</a>
%s''' % (city, base_url, random.uniform(0.0, 1.0), t, main, timestamp)
            ret = process_reply(
                {'chat_id': chat_id, 'parse_mode': 'html', 'text': res, 'disable_web_page_preview': False})
            log.info('%s' % ret)

            forecast = openweathermap.get_forecast()
            if forecast:
                s = ''
                for f in forecast:
                    s += '%s — <b>%s°C</b> %s %s\n' % f
                ret['add'] = [process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': s})]
                print(s)

            return ret

        return render_template('weather.html', temp=t, base_url=base_url, ico=ico, main=main,
                               city=city, description=description, timestamp=timestamp, details=details)
    else:
        log.error('Failed to get current weather')
        abort(500)


currencies = [
    ('rub', b'\xf0\x9f\x87\xb7\xf0\x9f\x87\xba', b'\xe2\x82\xbd'),
    ('usd', b'\xf0\x9f\x87\xba\xf0\x9f\x87\xb8', b'\x24'),
    ('eur', b'\xf0\x9f\x87\xaa\xf0\x9f\x87\xba', b'\xe2\x82\xac'),
    ('inr', b'\xf0\x9f\x87\xae\xf0\x9f\x87\xb3', b'\xe2\x82\xb9'),
    ('chf', b'\xf0\x9f\x87\xa8\xf0\x9f\x87\xad', b'\xe2\x82\xa3'),
    ('gbp', b'\xf0\x9f\x87\xac\xf0\x9f\x87\xa7', b'\xc2\xa3'),
    ('jpy', b'\xf0\x9f\x87\xaf\xf0\x9f\x87\xb5', b'\xc2\xa5'),
    ('uah', b'\xf0\x9f\x87\xba\xf0\x9f\x87\xa6', b'\xe2\x82\xb4'),
    ('kzt', b'\xf0\x9f\x87\xb0\xf0\x9f\x87\xbf', b'\xe2\x82\xb8'),
    ('byn', b'\xf0\x9f\x87\xa7\xf0\x9f\x87\xbe', b'Br'),
    ('try', b'\xf0\x9f\x87\xb9\xf0\x9f\x87\xb7', b'\xe2\x82\xba'),
    ('cny', b'\xf0\x9f\x87\xa8\xf0\x9f\x87\xb3', b'\xe5\x85\x83'),
    ('aud', b'\xf0\x9f\x87\xa6\xf0\x9f\x87\xba', b'\x00\x24'),
    ('cad', b'\xf0\x9f\x87\xa8\xf0\x9f\x87\xa6', b'\x00\x24'),
    ('pln', b'\xf0\x9f\x87\xb5\xf0\x9f\x87\xb1', b'Z\xc5\x82'),
    ('czk', b'\xf0\x9f\x87\xa8\xf0\x9f\x87\xbf', b'K\xc4\x8d'),
]

_ISOs = ['USD', 'EUR', 'INR', 'CHF', 'GBP', 'JPY', 'UAH', 'KZT', 'BYN', 'TRY', 'CNY', 'AUD', 'CAD', 'PLN', 'CZK', 'RUB']


@app.route('/currency/<args>', methods=['GET'])
def currency_f(chat_id=None, who=None, args=None, cmd=None):
    keyboard = None
    iso = args
    if not iso:
        buttons = []
        for cur in currencies[1:]:
            buttons.append({'text': '%s %s' % (cur[1].decode('utf-8'), cur[0].upper()),
                           'callback_data': '/currency %s' % cur[0]})

        blen3 = len(buttons) / 4
        keyboard = {'inline_keyboard': [
            buttons[:int(blen3)],
            buttons[int(blen3):int(2 * blen3)],
            buttons[int(2 * blen3):int(3 * blen3)],
            buttons[int(3 * blen3):],
        ]}

        resp = 'Select currency:'
    else:
        resp = fmt = flag = sym = rate = None

        rub = currencies[0]
        rub_sym = rub[2].decode('utf-8')

        iso = iso.lower()
        if iso == 'rub':
            flag = rub[1].decode('utf-8')
            resp = '%s 1 %s is 1 %s %s, dude!' % (flag, rub_sym, rub_sym, flag)
        if iso == 'rur':
            flag = rub[1].decode('utf-8')
            resp = '%s 1 RUR is 1000 %s %s, dude!' % (flag, rub_sym, flag)
        else:
            # rate = cbr.currency_rate(iso)
            rates = currencylayer.get_exchange_rate(config.Config.CURRENCYLAYER_KEY, _ISOs, 'RUB')
            rate = rates.get(iso)
            if rate:
                cur = next((x for x in currencies if x[0] == iso), None)
                flag = '%s ' % cur[1].decode('utf-8') if cur else ''
                sym = cur[2].decode('utf-8') if cur else iso.upper()
                fmt = '%s %s %s = %.2f %s ' + rub[1].decode('utf-8')
            else:
                resp = 'I don\'t know <i>%s</i>' % iso.upper()

        if not resp:
            resp = fmt % (flag, rate[0], sym, rate[1], rub_sym)

    if chat_id:
        response = {'chat_id': chat_id, 'parse_mode': 'html', 'text': resp}
        if keyboard:
            response['reply_markup'] = json.dumps(keyboard)

        return process_reply(response)
    return '<h1>%s</h1>' % resp


@app.route('/now')
def now_f(chat_id=None, who=None, args=None, cmd=None):
    now = datetime.datetime.now()
    resp = '%s UTC\n%i' % (now.strftime('%a %b %d %T.%f %Y'), now.timestamp())

    if chat_id:
        return process_reply({'chat_id': chat_id, 'text': resp})
    return '<h1>%s</h1>' % resp


@app.route('/traffic')
def nn_traffic_f(chat_id=None, who=None, args=None, cmd=None):
    res = nn_traffic.current_traffic()
    if res is None:
        res = ('', 'No traffic data :(')
    if chat_id:
        if app.config.get('HEROKU_APP_NAME'):
            base_url = 'https://%s.herokuapp.com/' % app.config.get('HEROKU_APP_NAME')
        else:
            base_url = '/'

        photo = '%straffic/ico/traffic%s.png' % (base_url, res[0])
        # if res[0] == 2:
        #    photo = '%s?1' % photo
        ret = process_reply({'method': 'sendPhoto',
                             'chat_id': chat_id,
                             'caption': 'Nizhniy Novgorod: %s' % res[1],
                             'photo': photo})
        map_photo = 'https://static-maps.yandex.ru/1.x/?lang=en_US&ll=%f,%f&size=360,360&z=12&l=map,trf&r=%s' % (43.996013, 56.281357, random.uniform(0.0, 1.0))
        ret['add'] = [process_reply({'method': 'sendPhoto', 'chat_id': chat_id, 'photo': map_photo})]
        return ret

    return send_from_directory('static/traffic-ico', 'traffic%s.png' % res[0])  # '<pre>%s</pre>' % resp


@app.route('/whoami')
def whoami_f(chat_id=None, who=None, args=None, cmd=None):
    if who is not None:
        t_id = who.get('id')
        first_name = who.get('first_name')
        username = who.get('username')
        last_name = who.get('last_name')

        name = first_name
        if username:
            name = '%s %s' % (name, username)
        if last_name:
            name = '%s %s' % (name, last_name)

        log.info('User #%s %s' % (t_id, name))

        user = models.BotUser.query.filter_by(telegram_id=t_id).first()
        if user is None:
            user = models.BotUser(telegram_id=t_id, name=name, huify=False, owm_city=config.Config.OWM_CITYID)
            db.session.add(user)
            db.session.commit()
        elif user.name is None:
            user.name = name
            db.session.commit()

    who_id = who.get('id') if who else None
    who_name = who.get('first_name') if who else 'Human'
    greet = None
    huify = False
    user = models.BotUser.query.filter_by(telegram_id=who_id).first()
    if user:
        if user.greet:
            greet = user.greet
            who_name = user.greet
        huify = user.huify

    resp = '''Hello, %s!
    
This feature is in development now.''' % who_name
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
        return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<pre>%s</pre>' % resp


def huify_f(chat_id, who, huify):
    changed = True
    user = models.BotUser.query.filter_by(telegram_id=who.get('id')).first()
    if user:
        changed = user.huify != huify
        user.huify = huify
    else:
        user = models.BotUser(telegram_id=who.get('id'), huify=huify)

    greet = user.greet if user.greet else who.get('first_name')

    if huify:
        if changed:
            resp = 'OK, %s, your messages will be huified now.' % greet
        else:
            resp = 'OK, %s, your messages are already being huified.' % greet
    else:
        if changed:
            resp = 'OK, %s, your messages will not be huified now.' % greet
        else:
            resp = 'OK, %s, your messages are already not being huified.' % greet

    db.session.add(user)
    db.session.commit()
    return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})


def huify_unhuify_f(chat_id=None, who=None, args=None, cmd=None):
    if cmd == '/huify':
        if args:
            return huify_text_f(chat_id, args, who)
        return huify_f(chat_id, who, True)
    return huify_f(chat_id, who, False)


@app.route('/whoareallthesefpeople')
def whoareallthesefpeople_f(chat_id=None, who=None, args=None, cmd=None):
    users = models.BotUser.query.all()
    if users and len(users):
        resp = 'Here they are:'
        for user in users:
            resp += '''
%s %s''' % (user.telegram_id, user.name)
    else:
        resp = 'No one is here'

    if chat_id:
        return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})
    return '<pre>%s</pre>' % resp


def beer_f(chat_id, who=None, args=None, cmd=None):
    greet = 'Human'
    if who.get('first_name'):
        greet = who.get('first_name')

    # holiday = wiki_calendar.get_drink_occasion()
    #if holiday:
    #    resp = '%s, %s\n%s' % (greet, emoji.CLINKING_BEER_MUGS, holiday.to_str())
    #else:
    #    resp = '%s, %s' % (greet, emoji.CLINKING_BEER_MUGS)
    resp = '%s, %s' % (greet, emoji.CLINKING_BEER_MUGS)
    return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})


def huify_text_f(chat_id, text, who=None):
    if text.lower() == 'нэвэльный':
        who_id = who.get('id')
        if who_id not in nevelny:
            nevelny[who_id] = -1
        nevelny[who_id] = (nevelny[who_id] + 1) % len(BLET)
        
        return process_reply({'chat_id': chat_id, 'method': 'sendSticker', 'sticker': BLET[nevelny[who_id]]})

    text = transcription.transcribe(text)
    text = wordify.wordify(text, randomize=False)
    # resp = text
    return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': text})


def huify_text_private_f(chat_id, text, who=None):
    text = transcription.transcribe(text)
    text = wordify.wordify(text, randomize=True)
    # resp = text
    return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': text})


def mynameis_f(chat_id, who, name, cmd):
    permaname = False

    user = models.BotUser.query.filter_by(telegram_id=who.get('id')).first()
    if user:
        if user.telegram_id == 396010103:  # or user.telegram_id == 314473825:
            permaname = True
    else:
        user = models.BotUser(telegram_id=who.get('id'))
        db.session.add(user)

    current = user.greet if user.greet else who['first_name']

    if name:
        if permaname:
            resp = '%s, %s' % (current, huificator.huify(name))
        else:
            user.greet = name
            resp = 'OK, %s' % name

        db.session.commit()

    else:
        resp = '%s, use /mynameis <i>greeting</i>' % current

    return process_reply({'chat_id': chat_id, 'parse_mode': 'html', 'text': resp})


def whereami_f(chat_id, who=None, args=None, cmd=None):
    keyboard = {
        'keyboard': [
            [{'text': 'Share location', 'request_location': True},
             {'text': 'Forget location'},
             {'text': 'Cancel'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True,
    }

    ret = process_reply({'chat_id': chat_id,
                         'text': 'Please select your location ' + b'\xf0\x9f\x8c\x90'.decode() +
                                 '\nOr not ' + b'\xf0\x9f\x91\x80'.decode(),
                         'reply_markup': json.dumps(keyboard)})
    # log.info(ret)
    return ret


def drink_f(chat_id, who=None, args=None, cmd=None):
    return process_reply({'chat_id': chat_id, 'method': 'sendSticker', 'sticker': 'CAADAgADiQAD12sEFvQF6xz18ISZAg'})


def do_find_location(chat_id, lat, long):
    print('lat=%f long=%f' % (lat, long))
    locs = yandexgeo.find_locations(lat, long, 5)

    keyboard2 = { 'remove_keyboard': True, }

    if locs:
        keyboard = {'inline_keyboard': [
            [{'text': x,
              'callback_data': '/location %f,%f,%s' % (lat, long, x)}] for x in locs],
        }
        #print(keyboard)

        ret = process_reply({'chat_id': chat_id, 'text': 'I found some places near you:',
                              'reply_markup': json.dumps(keyboard)})
        ret['add'] = [process_reply({'chat_id': chat_id, 'text': 'Please select one.',
                              'reply_markup': json.dumps(keyboard2)})]
        return ret
    else:
        return process_reply({'chat_id': chat_id, 'text': 'Can\'t find you ' + b'\xf0\x9f\x98\x9e'.decode(),
                              'reply_markup': json.dumps(keyboard2)})


def test_img_f(chat_id, who=None, args=None, cmd=None):
    # keyboard = {'inline_keyboard': [
    #    [{'text': '1', 'callback_data': '/weather'},
    #     {'text': '2', 'callback_data': '/traffic'}]
    # ]}
    keyboard = {
        'keyboard': [
            [{'text': 'Share location', 'request_location': True},
             {'text': 'Cancel'}]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True,
    }

    ret = process_reply({'chat_id': chat_id, 'text': 'test',
                         'reply_markup': json.dumps(keyboard)})
    # log.info(ret)
    return ret


commands = {
    '/help': start_f,
    '/start': start_f,
    '/whoami': whoami_f,
    '/whereami': whereami_f,
    '/weather': weather_f,
    '/traffic': nn_traffic_f,
    '/now': now_f,
    '/currency': currency_f,
    '/test': test_img_f,
    '/whoareallthesefpeople': whoareallthesefpeople_f,
    '/whoarethesefpeople': whoareallthesefpeople_f,
    '/huify': huify_unhuify_f,
    '/unhuify': huify_unhuify_f,
    '/mynameis': mynameis_f,
    '/drink': drink_f,#beer_f,
}


def process_message(message):
    chat_id = message['chat']['id']

    if 'location' in message:
        return do_find_location(chat_id, message['location']['latitude'], message['location']['longitude'])

    req = message['text'].split(maxsplit=1)
    if len(req) > 1:
        (command, args) = req
    else:
        command = req[0]
        args = None

    if command.endswith('@kapnuu_bot'):
        command = command[:-11]

    if command.startswith('/'):
        command = command.lower()
    elif 'chat' in message and 'type' in message['chat'] and message['chat']['type'] == 'supergroup':
        return

    if command in commands:
        result = commands[command](chat_id, message['from'], args, command)
        if result:
            print('result: %s' % result)
            if 'add' in result:
                add = result.get('add')
                result.pop('add')
                requests.request('post', '%s%s' % (URL, result['method']), data=result)
                print('%s' % add)
                if len(add) == 1:
                    result = add[0]
                else:
                    for m in add[:-1]:
                        requests.request('post', '%s%s' % (URL, m['method']), data=m)
                    result = add[-1]
            return result

    text = message['text'].lower()
    if text == 'cancel':
        keyboard = {
            'remove_keyboard': True,
        }
        result = process_reply({'chat_id': chat_id, 'text': 'As you want', 'reply_markup': json.dumps(keyboard)})
    elif text == 'forget location':
        # TODO forget user location
        keyboard = {
            'remove_keyboard': True,
        }
        result = process_reply({'chat_id': chat_id, 'text': 'As you want', 'reply_markup': json.dumps(keyboard)})
    elif text == 'замучить котов' \
            or text == 'мучить котов' \
            or text == 'torture cats':
        result = process_reply({'chat_id': chat_id, 'text': 'КОТОВ МУЧИТЬ НЕЛЬЗЯ, СУЧКА!!'})
    elif text == emoji.BEER_MUG or text == emoji.CLINKING_BEER_MUGS:
        result = beer_f(chat_id, message['from'])
    else:
        t_id = message['from'].get('id')

        user = models.BotUser.query.filter_by(telegram_id=t_id).first()
        if user and user.huify:
            result = huify_text_private_f(chat_id, message['text'], message['from'])
        else:
            result = process_reply({'chat_id': chat_id, 'text': 'You said: %s. WTF?' % message['text']})

    return result


@app.route('/hook', methods=['GET', 'POST'])
def process_request2():
    return process_request()
