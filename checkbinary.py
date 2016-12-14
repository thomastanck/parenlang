#!/usr/bin/env python3
import parenlang

hashset = set()

for i in range(65536):
    binary_repr = '{0:016b}'.format(i)
    try:
        p = parenlang.BinaryReprParser(binary_repr).parse()
    except:
        # print('0'*(8-len(binary_repr))+binary_repr, 'illegal', 'illegal', binary_repr, 'illegal', '-')
        continue
    b = str(p.bintree_form())
    r = p.binary_repr()
    s = p.shorthand_form()
    h = hash(s)
    s = str(s)
    if h in hashset:
        print('collision', s, '{:016X}'.format(h))
    else:
        hashset.add(h)
    h = '{:016X}'.format(h)
    print(' | '.join([
        binary_repr.rjust(16,'0'),
        #str(p).ljust(60),
        #b.ljust(60),
        #r.rjust(16),
        s.ljust(60),
        #'N' if b==s else 'Y',
        h,
        ]))
