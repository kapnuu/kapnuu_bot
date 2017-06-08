import re

vowels = ['a', 'e', 'i', 'o', 'u', 'y']

opens = ['эй', 'и', 'ай', 'оу', 'ью', 'ай']

closeds = ['э', 'э', 'и', 'о', 'у', 'и']

syllable_re = re.compile('([^aeiouy]*[aeiouy]?)')

consonants2_re = re.compile('^[^aeiouy](?:[^aeiouy]|$)')

replaces_re = [
    # в открытом слоге
    # эй в начале слова и после гласных,
    # ей после согласных
    # (re.compile('^a'), ''),
    (re.compile('cia$'), 'шия'),
    (re.compile('wa[^$]'), 'уо'),
    (re.compile('c(?=[eiy])'), 'с'),
    (re.compile('g(?=[eiy])'), 'дж'),

    (re.compile('cei'), 'сэй'),
    (re.compile('ough'), 'аф'),
    (re.compile('oo'), 'у'),
    # (re.compile('e$'), ''),

    # (re.compile('^mack'), 'макк'),
]

replaces_before = [
    ('eigh', 'эй'),
    ('mack', 'макк'),
    ('ough', 'аф'),

    ('cei', 'сэй'),
    ('sch', 'ск'),
    ('ere', 'ир'),
    ('igh', 'ай'),
    ('our', 'аур'),
    ('phy', 'фи'),

    ('ey', 'и'),
    ('ch', '♥ч'),
    ('sh', '♥ш'),
    ('th', '♥з'),
    ('ph', '♥ф'),
    ('wh', '♥в'),
    ('ck', '♥к'),
    ('kn', '♥н'),
    ('wr', '♥р'),
    ('gh', '♥ф'),
    ('gg', 'гг'),
    ('qu', 'кв'),
    ('eu', 'ю'),  # 'ью' after consonants
    ('ew', 'ю'),  # 'ью' after consonants
    ('al', 'ол'),
    ('dg', 'дж'),
    ('ow', 'оу'),
    ('oo', 'у'),
]

replaces = [

    ('b', 'б'),
    ('c', 'к'),  # exclude c[ei]
    ('d', 'д'),
    ('f', 'ф'),
    ('h', 'х'),
    ('g', 'г'),
    ('j', 'дж'),
    ('k', 'к'),
    ('l', 'л'),
    ('m', 'м'),
    ('n', 'н'),
    ('p', 'п'),
    ('q', 'к'),
    ('r', 'р'),
    ('s', 'с'),
    ('t', 'т'),
    ('v', 'в'),
    ('w', 'в'),
    ('x', 'кс'),
    ('z', 'з'),
]


def split_to_syllables(word):
    cut = -1
    all_syls = syllable_re.findall(word)
    if all_syls and len(all_syls) > 0:
        for i in range(0, len(all_syls)-2):
            if consonants2_re.match(all_syls[i + 1]):
                if any(x in vowels for x in all_syls[i + 1]):
                    all_syls[i] = '%s%s' % (all_syls[i], all_syls[i + 1][0])
                    all_syls[i + 1] = all_syls[i + 1][1:]
                else:
                    all_syls[i] = '%s%s' % (all_syls[i], all_syls[i + 1])
                    all_syls[i + 1] = None

                if not all_syls[i + 1]:
                    cut = -2  # this may be only at the end
    return all_syls[:cut]


def transcribe(word):
    ret = ''

    for r in replaces_before:
        word = word.replace(r[0], r[1])
    for r_re in replaces_re:
        if r_re[0].search(word):
            word = r_re[0].sub(r_re[1], word)

    syllables = split_to_syllables(word)
    for syl_idx, syl in enumerate(syllables):
        if syl_idx == len(syllables) - 1:
            if syl.endswith('e'):
                syl = syl[:-1]

        is_open = False
        v = next((x for x in syl if x in vowels), None)
        if v:
            idx = vowels.index(v)
            is_open = syl[-1] in vowels

        for r in replaces:
            syl = syl.replace(r[0], r[1])

        if is_open:
            syl = syl.replace(v, opens[idx])
        elif v:
            syl = syl.replace(v, closeds[idx])

        ret += syl

    return ret.replace('♥', '')
