#!/usr/bin/env python3
import parenlang

for i in range(256):
    binary_repr = '{0:08b}'.format(i)
    try:
        p = parenlang.BinaryReprParser(binary_repr).parse()
    except:
        print('0'*(8-len(binary_repr))+binary_repr, 'illegal', 'illegal', binary_repr, 'illegal', '-')
        continue
    b = str(p.bintree_form())
    r = p.binary_repr()
    s = str(p.shorthand_form())
    print('0'*(8-len(binary_repr))+binary_repr, str(p), b, r, s, 'N' if b==s else 'Y')
