import datetime

_lunar_images = [
    ('\U0001f311', 'new-moon'),
    ('\U0001f312', 'waxing-cresent'),
    ('\U0001f313', 'first-quarter'),
    ('\U0001f314', 'waxing-gibbous'),
    ('\U0001f315', 'full-moon'),
    ('\U0001f316', 'waning-gibbous'),
    ('\U0001f317', 'last-quarter'),
    ('\U0001f318', 'waning-cresent'),
]


def moonphase_n(date):
    new_moon = datetime.datetime(2017, 6, 24, 5, 32)

    cycle = 29.5305882
    phase_length = cycle / 8

    diff = (date - new_moon).days
    ldays = (diff + phase_length / 2) % cycle
    # print('%s %s' % (date.day, ldays))
    current_phase = ldays * (8 / cycle)
    return int(current_phase + 0.5) % 8


def moonphase(date):
    return _lunar_images[moonphase_n(date)]


if __name__ == '__main__':
    print(moonphase(datetime.datetime.now())[1])

#    with open('lunar.htm', 'wt', encoding='utf-8') as f:
#        for d in range(1, 32):
#            res = moonphase(datetime.datetime(2017, 7, d))
#            f.write('July %s &mdash; %s %s<br/>' % (d, res[0], res[1]))

