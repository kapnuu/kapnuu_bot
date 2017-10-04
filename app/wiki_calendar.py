import requests
import re
import random
import datetime

_re_curly_brackets = re.compile('(.*){{([^\}]+)\}\}(.*)')
_re_square_brackets = re.compile('^(.*)\[\[([^\]]*)\]\](.*)$')


def extract_from_curly_brackets(text, replace_tag, replace_key):
    m = _re_curly_brackets.match(text)
    while m:
        ok = False
        g = m.groups()
        s = g[1]
        ss = s.split('|')
        tag = ss[0]
        if tag == replace_tag:
            for item in ss[1:]:
                vv = item.split('=')
                if vv[0] == replace_key:
                    text = '%s%s%s' % (g[0], vv[1], g[2])
                    ok = True
                    break

        if not ok:
            break
        m = _re_curly_brackets.match(text)
    return text


def extract_from_square_brackets(text, regex):
    m = regex.match(text)
    while m:
        g = m.groups()
        s = g[1].split('|')
        text = '%s%s%s' % (g[0], s[1] if len(s) == 2 else s[0], g[2])
        m = regex.match(text)
    return text


_flags = {
    'Россия': b'\xf0\x9f\x87\xb7\xf0\x9f\x87\xba'.decode('utf-8')
}


_holidays = [
    b'\xF0\x9F\x90\x8E'.decode('utf-8'),  # horse
    b'\xF0\x9F\x90\x92'.decode('utf-8'),  # monkey
    b'\xF0\x9F\x90\xB1'.decode('utf-8'),  # cat face
    b'\xF0\x9F\x90\xB0'.decode('utf-8'),  # rabbit face
    b'\xF0\x9F\x90\xBB'.decode('utf-8'),  # bear face
    b'\xF0\x9F\x90\xBC'.decode('utf-8'),  # panda face
    b'\xF0\x9F\x98\x9D'.decode('utf-8'),  # face with stuck-out tongue and tightly-closed eyes
    b'\xF0\x9F\x98\x9C'.decode('utf-8'),  # face with stuck-out tongue and winking eye
    b'\xF0\x9F\x98\xB8'.decode('utf-8'),  # grinning cat face with smiling eyes
    b'\xE2\x9C\x8C'.decode('utf-8'),  # victory hand
    b'\xE2\x9C\x8B'.decode('utf-8'),  # raised hand
    b'\xF0\x9F\x98\x8E'.decode('utf-8'),  # smiling face with sunglasses
    b'\xF0\x9F\x8E\x8A'.decode('utf-8'),  # confetti ball
    b'\xF0\x9F\x8E\x88'.decode('utf-8'),  # balloon
    b'\xF0\x9F\x8E\x89'.decode('utf-8'),  # party popper
    b'\xF0\x9F\x91\x8F'.decode('utf-8'),  # clapping hands sign
    b'\xF0\x9F\x8D\xB7'.decode('utf-8'),  # wine glass
]

_beer_mug = b'\xF0\x9F\x8D\xBA'.decode('utf-8')
_clinking_beer_mugs = b'\xF0\x9F\x8D\xBB'.decode('utf-8')
_shortcake = b'\xF0\x9F\x8D\xB0'.decode('utf-8')
_birthday_cake = b'\xF0\x9F\x8E\x82'.decode('utf-8')
_scull = b'\xF0\x9F\x92\x80'.decode('utf-8')


class National:
    re_flag = re.compile('{{Флаг(?:ификация)?\|(.*)\}\}')

    def __init__(self, text):
        self.ok = False
        self.countries = []
        self.holidays = []

        ss = text.split('—')

        for s in ss[0].split(','):
            s = s.strip()
            m = self.re_flag.match(s)
            if m:
                self.countries.append(m.groups()[0].strip())
            elif s.startswith('[['):
                self.countries.append(extract_from_square_brackets(s, _re_square_brackets))

        if len(ss) == 2:
            self.add(ss[1])
            # print('%s' % self.holidays)
            self.ok = self.countries is not None and self.holidays is not None
        else:
            self.ok = True

    def add(self, text):
        self.holidays.append(extract_from_square_brackets(text.strip(), _re_square_brackets).strip('.'))

    def to_str(self):
        icons = [_beer_mug, random.choice(_holidays), random.choice(_holidays), random.choice(_holidays)]
        random.shuffle(icons)
        icons = ''.join(icons)
        if len(self.countries) == 1:
            return '%s%s празднует %s%s' % (_flags[self.countries[0]] if self.countries[0] in _flags else '',
                                            self.countries[0], random.choice(self.holidays), icons)
        return '%s празднуют %s%s' % (', '.join(self.countries), random.choice(self.holidays), icons)


class Religion:
    def __init__(self, text):
        text = text.replace('([[переходящее празднование]] в 2017 г.)', '')
        self.holiday = extract_from_square_brackets(text, _re_square_brackets)[:-1]

    def to_str(self):
        return 'Верующие отмечают %s' % self.holiday


class NameDay:
    names = []

    def add(self, text):
        m = _re_square_brackets.match(text)
        if m:
            g = m.groups()
            s = g[0].split('|')
            self.names.append(s[1] if len(s) == 2 else s[0])

    def to_str(self):
        icons = [_shortcake, random.choice(_holidays), random.choice(_holidays), random.choice(_holidays)]
        random.shuffle(icons)
        icons = ''.join(icons)
        ii = list(range(0, len(self.names)))
        random.shuffle(ii)
        return '%sИменины празднуют %s%s' % (_birthday_cake, ', '.join([self.names[i] for i in ii]), icons)
        # return 'Именины празднуют ' + ', '.join(self.names)


class Person:
    regex = re.compile('^\[\[([^\]]+)\]\](.*)$')
    regex2 = re.compile('(.*)\[\[([^\]]+)\]\](.*)')
    regex3 = re.compile('(.*){{([^\]]+)\}\}(.*)')

    def __init__(self, text, birth):
        self.people = []
        self.birth = birth
        m = self.regex.match(text)
        if m:
            g = m.groups()
            s = g[0].split('|')
            self.year = s[1] if len(s) == 2 else s[0]

            if len(g[1]):
                self.add(g[1])

    def add(self, text):
        if text[0].isspace():
            text = text[3:]
        text = extract_from_square_brackets(text, self.regex2)
        text = extract_from_square_brackets(text, self.regex3)
        self.people.append(text[:-1])

    def to_str(self):
        icons = [_shortcake, random.choice(_holidays), random.choice(_holidays), random.choice(_holidays)]
        random.shuffle(icons)
        icons = ''.join(icons)
        person = random.choice(self.people)
        if self.birth:
            return '%sHappy Birthday (%s) %s%s' % (_birthday_cake, self.year, person, icons)
        else:
            return '%sR.I.P. (%s) %s' % (_scull, self.year, person)


_months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
           'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

holidays = []
nameday = NameDay()
births = []
deaths = []


def download(day, month):
    r = requests.get('https://ru.wikipedia.org/w/index.php?title=%s_%s&action=raw' % (day, _months[month - 1]))
    if r.ok:
        answer = r.text
        with open('%s_%s.htm' % (day, month), 'wt', encoding='utf-8') as outp:
            outp.write(answer)
        return answer


NONE = 0
NATIONAL = 1
RELIGION = 2
NAMEDAY = 3
EVENTS = 4
BIRTHS = 5
DEATHS = 6
STOP = 7


def process(wikipage):
    last_year = None
    last_holiday = None

    state = NONE
    for line in wikipage.split('\n'):
        if not line:
            continue

        line = extract_from_curly_brackets(line, 'не переведено', 'текст')
        try:
            if state == NATIONAL:
                if line[0] == '*':
                    if line[1] == '*' and last_holiday:
                        last_holiday.add(line[3:])
                    else:
                        item = National(line[2:])
                        if item.ok:
                            holidays.append(item)
                            last_holiday = item

            if state == RELIGION:
                if line[0] == '*':
                    pass
                    #holidays.append(Religion(line[2:]))

            if state == NAMEDAY:
                if line.startswith('* '):
                    nameday.add(line[2:])

            if state == BIRTHS:
                if line.startswith('* '):
                    last_year = Person(line[2:], True)
                    births.append(last_year)
                elif line.startswith('** '):
                    last_year.add(line[3:])

            if state == DEATHS:
                if line.startswith('* '):
                    last_year = Person(line[2:], False)
                    deaths.append(last_year)
                elif line.startswith('** '):
                    last_year.add(line[3:])

            if line == '== Праздники и памятные дни ==':
                state = NATIONAL
            elif line == '=== [[Файл:P religion world.svg|30px]] Религиозные ===':
                state = RELIGION
            elif line == '=== Именины ===':
                state = NAMEDAY
            elif line == '== События ==':
                state = EVENTS
            elif line == '== Родились ==':
                state = BIRTHS
            elif line == '== Скончались ==':
                state = DEATHS
            elif line == '== Приметы ==':
                state = STOP
        except Exception as e:
            print('%s' % e)
            pass


def get_drink_occasion():
    with open('e:\\#saved\\dev\\#python\\wiki-calendar\\12_8.htm', 'rt', encoding='utf-8') as inp:
        process(inp.read())

    items = [
        random.choice(holidays),
        random.choice(births),
        random.choice(deaths),
        # nameday
    ]

    return random.choice(items)


if __name__ == '__main__':
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    #print('%s %s' % (now.day, now.month))
    #answer = download(now.day, now.month)
    #answer = download(15, now.month)
    #if answer:
    #    process(answer)
    choice = get_drink_occasion()
    print('%s %s' % (choice.to_str(), choice.icon))

    with open('output.txt', 'wt', encoding='utf-8') as outp:
        for item in holidays:
            outp.write(item.to_str())
            outp.write('\n')
        outp.write(nameday.to_str())
        outp.write('\n')
        for item in births:
            outp.write(item.to_str())
            outp.write('\n')
        for item in deaths:
            outp.write(item.to_str())
            outp.write('\n')

if __name__ == '__ma1in__':
    # print(extract_from_curly_brackets('* {{Флагификация|Египет}} — {{не переведено|есть=:en:Flooding of the Nile|надо='
    #                                  'Разлив Нила|текст=День разлива Нила|язык=англ.|nocat=1}}.', 'не переведено',
    #                                  'текст'))
    line = '* {{Флагификация|Канада}}, [[Новая Шотландия]] — Национальный день.'
    item = National(line[2:])
    print(item.to_str())
