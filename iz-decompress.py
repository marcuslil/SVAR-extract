# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 19:58:07 2014

@author: marcus
"""

from subprocess import call
import os

from os import listdir
from os.path import isfile, join, getsize


mypath = '/sharedwine/default/drive_c/SVBEF70/hdbas/'

def fill3(s):
    if type(s) == str:
        s = ord(s)
    return hex(s)[2:].zfill(2)

splitter = '\x00\x00SPIS\x1aLH5'

def uncompress(fname):
    fname1 = join(mypath, fname)
    f = open(fname1, 'r')
    s = f.read()
    f.close()
    print fname1

    tot_len = 0
    res = []
    for i in range(4*3, len(s), 4):
        a = 0
        for x in range(4):
            a += ord(s[i + x]) * 256**x
        res.append(a)
#        print map(fill3, s[i:i +4]), a
    
        
    fname = join('/home/marcus/Skrivbord/SVAR-unpack/ex',fname)
    f1 = open(fname, 'w')
    f1.write(str(res))
    f1.close()


files = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for fname in files:
    if fname[-3:] == '.iz' or fname[-2:] == '.p' or fname[-3:] == '.pz':
        uncompress(fname)
