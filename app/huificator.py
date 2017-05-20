import re

hueplace = {
    'а': 'я',
    'е': 'е',
    'ё': 'ё',
    'и': 'и',
    'о': 'ё',
    'у': 'ю',
    'ы': 'и',
    'э': 'е',
    'ю': 'ю',
    'я': 'я'
}

huexp = re.compile('^[бвгджзйклмнпрстфхцчшщъь]*([аеёиоуыэюя])(.*)')

huexceptions = {
    'хуификатор': 'Hmm?',
    'путин': 'Mr. President',
    'россия': 'https://en.wikipedia.org/wiki/Russia',
}


def huify(word):
    w = word = word.lower()
    if w in huexceptions:
        word = huexceptions[w]
    else:
        if w.startswith('ху') and len(w) > 5:
            w = word[2:]
        m = huexp.match(w)
        if m:
            g = m.groups()
            if len(g) == 2:
                if g[0] in hueplace:
                    word = 'ху%s%s' % (hueplace[g[0]], g[1])
    return word
