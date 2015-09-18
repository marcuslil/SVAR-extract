# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 19:58:07 2014

@author: marcus
"""

from subprocess import call
import os

from os import listdir
from os.path import isfile, join, getsize



def fill3(s):
    if type(s) == str:
        s = ord(s)
    return hex(s)[2:].zfill(2)

splitter = '\x00\x00SPIS\x1aLH5'
header = [0, 0, 0, 0, 0, 0, 0x10, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def uncompress(fname):
    print fname
    f = open(fname, 'r')
    s = f.read()
    f.close()

        
#    fname2 = join('/home/marcus/ex',fname.split('/')[-1])
#    f1 = open(fname2, 'w')
    #print map(fill3, s[:30])
    n = ord(s[6])
    print map(fill3, s[:16])
    assert map(ord,s[:16]) == header
    oofa = False
    x_last = 0
    nrs = 0
    p = None
    #while n < len(s):
    while n < 0x100:
        x = 0
        if not oofa:
            if p != None:
                print hex(p)
            p = 1
            x = ord(s[n]) + ord(s[n+1]) * 256 + ord(s[n+2]) * 256 **2 + ord(s[n+3]) * 256 **3
            print hex(n), map(fill3, s[n:n+4]), hex(x), x - x_last
            if x == 0x1010101 or ord(s[n+3]) != 0:
                stop
            x_last = x
            n += 4
            nrs += 1
        
        
        if x != 0x5027a7:
            oofa = False        
            off = ord(s[n+0]) + ord(s[n+1]) * 256 * 1
            if off >= 0xfa00:
                oofa = True
                if off >= 0xfa05:
                    stop
            l = off - 2
            if l> 10:
                l = 10
            print hex(n), map(fill3, s[n+0:n+2]), off, '>' + ''.join(map(fill3, s[n+2:n+l+2])) + '<'
            n2 = n + 2
            n += off
            ss = ''
            while n2 < n:
                if ord(s[n2]) == 0:
                    a = 3
                elif ord(s[n2]) == 255:
                    a = 5
                else:
                    a = 1
                #ss = ss + ' ' + ''.join(map(fill3, s[n2:n2+a]))
                n2 += a
                p += 1
            assert n == n2, (n,n2,hex(ord(s[n-1])))
        #print ss
    assert n  == len(s), (n, len(s))
    print nrs
#    f1.write(s[24:])
#    f1.close()
    

mypath = ['/sharedwine/default/drive_c/SVBEF70/cdbas/',
          '/sharedwine/default/drive_c/SVBEF70/hdbas/']


uncompress(join(mypath[0],'ma70reg1.b1'))

stop

n = 0
for path in mypath:
    files = [ f for f in listdir(path) if isfile(join(path,f)) ]
    for fname in files:
        if fname[-3:] == '.b1':
            uncompress(join(path, fname))
