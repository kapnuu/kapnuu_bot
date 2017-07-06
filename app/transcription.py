import re

vowels = ['a', 'e', 'i', 'o', 'u', 'y']

opens = ['эй', 'и', 'ай', 'оу', 'ью', 'ай']

closeds = ['э', 'э', 'и', 'о', 'а', 'и']

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
    (re.compile('^y(?=[aeiouy])'), 'й'),
    (re.compile('(?<=[aeiouy])y$'), 'й'),
    # (re.compile('y$'), 'и'),

    (re.compile('tion$'), 'шэн'),

    (re.compile('^u(?=[r])'), 'ё'),

]

exceptions = [
    ('you', 'ю'),
    ('the', 'зэ'),
    ('was', 'воз'),
    ('have', 'хэв'),
    ('there', 'зээр'),
    ('were', 'вёр'),
    ('where', 'вээр'),
    ('what', 'вот'),
    ('a', 'э'),
    ('to', 'ту'),
    ('maybe', 'мэйби'),
    ('your', 'йёр'),
    ('one', 'ван'),
    ('two', 'ту'),
    ('three', 'сри'),
    ('four', 'фор'),
    ('seven', 'севэн'),
    ('twenty', 'твэнти'),
    ('thirty', 'сёти'),
    ('fourty', 'фоти'),
    ('fifty', 'фифти'),
    ('sixty', 'сиксти'),
    ('seventy', 'севенти'),
    ('eighty', 'эйти'),
    ('ninety', 'найнти'),
    ('hundred', ''),
    ('thousand', ''),
    ('only', 'онли'),
    ('do', 'ду'),
    ('young', 'йанг'),
    ('woman', 'вумэн'),
    ('every', 'еври'),
    # ('try', ''),
    ('ready', 'рэди'),
    ('way', 'вэй'),
    ('who', 'ху'),
    ('any', 'эни'),
]


replaces_before = [
    ('eigh', 'эй'),
    ('mack', 'макк'),
    ('ough', 'аф'),
    ('teen', 'тин'),

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
    word = word.lower()

    exc = next((x[1] for x in exceptions if x[0] == word), None)
    if exc:
        return exc

    ret = ''

    for r in replaces_before:
        word = word.replace(r[0], r[1])
    for r_re in replaces_re:
        if r_re[0].search(word):
            word = r_re[0].sub(r_re[1], word)

    syllables = split_to_syllables(word)
    for syl_idx, syl in enumerate(syllables):
        if syl_idx == len(syllables) - 1:
            if syl.endswith('e') and syl_idx > 0:
                syl = syl[:-1]
                # print(syl)

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

if __name__ == '__main__':
    print(transcribe(input('Enter word: ')))

# http://www.alleng.ru/mybook/2read/U.htm
