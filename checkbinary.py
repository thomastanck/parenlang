#!/usr/bin/env python3
import parenlang

import random

hashset = set()
parenset = set()

def random_paren(k, r=0):
    if k == 0:
        return ''
    prob_right = r * (k + r + 2) / 2 / k / (r + 1)
    is_right = random.random() <= prob_right
    if is_right:
        return ')' + random_paren(k-1, r-1)
    else:
        return '(' + random_paren(k-1, r+1)

def test_paren_hash(p):
    b = str(p.bintree_form())
    r = p.binary_repr()
    s = p.shorthand_form()
    h = hash(s)
    if h in hashset:
        print('collision', str(s), '{:016X}'.format(h))
    else:
        hashset.add(h)
    if s in parenset:
        print('paren collision', str(s), '{:016X}'.format(h))
    else:
        parenset.add(s)
    h = '{:016X}'.format(h)
    s = str(s)
    print(' | '.join([
        # binary_repr.rjust(16,'0'),
        #str(p).ljust(60),
        #b.ljust(60),
        #r.rjust(16),
        s.ljust(100),
        #'N' if b==s else 'Y',
        h,
        ]))

for i in range(256):
    binary_repr = '{0:016b}'.format(i)
    try:
        p = parenlang.BinaryReprParser(binary_repr).parse()
    except:
        # print('0'*(8-len(binary_repr))+binary_repr, 'illegal', 'illegal', binary_repr, 'illegal', '-')
        continue
    test_paren_hash(p)

# for i in range(65536):
#     binary_repr = '{0:016b}'.format(i)
#     try:
#         p = parenlang.BinaryReprParser(binary_repr).parse()
#     except:
#         # print('0'*(8-len(binary_repr))+binary_repr, 'illegal', 'illegal', binary_repr, 'illegal', '-')
#         continue
#     test_paren_hash(p)

trials = 500
for i in range(trials):
    p_str = '(' + random_paren(98) + ')'
    p = parenlang.Parser(p_str).parse()[0]
    test_paren_hash(p)
