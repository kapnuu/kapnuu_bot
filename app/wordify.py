from app import huificator
import random


def _capitalize(s, idx):
    return '%s%s%s' % (s[0:idx], s[idx].upper(), s[idx+1:])


def _processword(word, uppers, randomize):
    if len(word) > 2 and (not randomize or random.randint(0, 1)):
        s = huificator.huify(word)
        if word.isupper():
            return s.upper()

        diff = len(s) - len(word)
        # print(s)
        # print(uppers)
        if uppers:
            for idx in uppers[::-1]:
                if idx != 0:
                    newidx = idx + diff
                else:
                    newidx = 0

                if newidx >= 0:
                    s = _capitalize(s, newidx)
                # print('%s %s' % (newidx, s))

            vocal = 2 - diff
            # print(vocal)
            if (vocal != 0) and (0 in uppers) and (vocal in uppers):
                s = _capitalize(s, 1)
        return s
    return word


def wordify(text, randomize=False):
    res = ''
    word = ''
    uppers = []
    for c in text:
        if c.isalpha():
            if c.isupper():
                uppers.append(len(word))
            word += c
        else:
            if word:
                res += _processword(word, uppers, randomize)
                word = ''
                uppers = []
            res += c

    res += _processword(word, uppers, randomize)
    return res


if __name__ == '__main__':
    print(wordify(input()))
