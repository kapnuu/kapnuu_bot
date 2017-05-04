import requests
import re
import logging

traffic_descriptions = [
    'Дороги свободны',
    'Дороги почти свободны',
    'Местами затруднения',
    'Местами затруднения',
    'Движение плотное',
    'Движение затруднённое',
    'Серьёзные пробки',
    'Многокилометровые пробки',
    'Город стоит',
    'Пешком быстрее',
]

log = logging.getLogger('app')

actuality = 30  # minutes


def get_traffic():
    ret = None
    r = requests.get('http://m.nn.ru')
    if r.status_code == 200:
        text = r.text
        g = re.search(r'([0-9]+)&nbsp;балл', text).groups()
        if len(g) > 0:
            idx = int(g[0])
            descr = None
            if 0 < idx <= len(traffic_descriptions):
                descr = traffic_descriptions[idx - 1]
            ret = (idx, descr)
    return ret
