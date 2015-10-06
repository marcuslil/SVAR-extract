# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 22:40:21 2014

@author: marcus
"""

from copy import copy

sort_string = u"\t\r\n !\"#$%&'()*+÷,-./0123456789:;<=>?_«\x83\x88\x8b\x93\x96¼½¾¨`|¦ªº~aáàâbcçdðeéèêëfghiíìïîjklmnoôóòpqrsßtÞuúùûvwxyýŸüz[]{}\x85§õåæäöØã´\xa0"
accents = ((u'é',u'e'), (u'è',u'e'),(u'ü',u'y'),(u'í',u'i'),(u'Ø',u'ö'),(u'ó',u'o'),(u'Ú',u'u'),(u'â',u'a'),(u'á',u'a'))

sort_index = [-1] * 256

for n, o in enumerate(sort_string):
    try:
        sort_index[ord(o.lower().encode('latin1'))] = n
    except:
        pass
    try:
        sort_index[ord(o.upper().encode('latin1'))] = n
    except:
        pass

sort_index_ignore_accents = copy(sort_index)

for accent in accents:
    n = ord(accent[1].lower().encode('latin1'))
    n = sort_index[n]
    o = ord(accent[0].lower().encode('latin1'))
    sort_index_ignore_accents[o] = n
    o = ord(accent[0].upper().encode('latin1'))
    sort_index_ignore_accents[o] = n

def compare(str1, str2, ignore_accents=False):
    assert type(str1) == bytes
    m = min(len(str1), len(str2))
    index = sort_index if not ignore_accents else sort_index_ignore_accents
    for n in range(m):
        s1 = index[str1[n]]
        assert s1 >= 0, ((bytes([str1[n]]).decode('latin1'), hex(str1[n])), str1)
        s2 = index[str2[n]]
        assert s2 >= 0, ((bytes([str2[n]]).decode('latin1'), hex(str2[n])), str2)
        if s1 > s2:
            return 1
        elif s2 > s1:
            return -1
    if len(str1) == len(str2):
        return 0
    elif len(str1) > len(str2):
        return 1
    else:
        return -1