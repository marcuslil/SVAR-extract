# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 19:58:07 2014

@author: marcus
"""

from common import *
from os.path import getsize, isdir
from os import listdir


def uncompress_i(fname, write = False):
    f = open(fname, 'r')

    header = read_i_header(f)
    if write:
        fname2 = join('ex',fname.split('/')[-1])
        f1 = open(fname2, 'w')

    print '/'.join(fname.split('/')[-3:]).ljust(30), 'e_size', hex(header['entry_size']).ljust(5), str(header['entry_size']).ljust(3), 'comp=' + ('1' if header['compressed'] else '0'), 'f_len=' + ('1' if header['fixed_length'] else '0'), 'data1:'+ str(header['data1']).zfill(7), 'start:'+ hex(header['start_pos'])[2:]

    if not header['compressed']:
        data = f.read()
        uncompressed_size = len(data)
        n = 0

        if write:
            f1.write(data)
            f1.close()
    else:
        n = 0
        uncompressed_size = 0
        while True:
            lh5_header = read_lh5_header(f)
            if lh5_header == None:
                break           
            if header['fixed_length']:
                assert lh5_header['uncompressed_size'] % header['entry_size'] == 0, (lh5_header['uncompressed_size'], header['entry_size'], lh5_header['uncompressed_size'] % header['entry_size'])
            uncompressed_size += lh5_header['uncompressed_size']
            if write or n == 0:
                s = check_output([lh5_bin, fname, str(lh5_header['uncompressed_size']), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
            if write:
                assert len(s) == lh5_header['uncompressed_size'], (len(s), lh5_header['uncompressed_size'])
                f1.write(s)
            if n == 0:
                data = s
                
            n += 1
            f.seek(lh5_header['next_header'])
            #break

        if write:
            f1.close()

    #if header['fixed_length']:
    #    assert uncompressed_size == header['entrys'] * header['entry_size']

    print 'data',map(hex, map(ord, data[:8])), data[8:12].replace('\x00', '!')            
    print 'tot_len:', hex(uncompressed_size), 'blocks:', hex(n), 'entrys:', hex(uncompressed_size/header['entry_size']), 'file_length', hex(getsize(fname))
   

mypaths = ['/sharedwine/default/drive_c/SVBEF70/',
          '/sharedwine/default/drive_c/SVBEF80/',
          '/sharedwine/default/drive_c/SVBEF1890',
          '/sharedwine/default/drive_c/Sveriges dödbok 1901-2009']
          
def list_files(mypath, endings):
    res = []
    for path in mypath:
        for dir in ['cdbas', 'hdbas']:
            path2 = join(path, dir)
            if isdir(path2):
                files = [ f for f in listdir(path2) if isfile(join(path2,f)) ]
                for fname in files:
                    fname2 = join(path2, fname)
                    for ending in endings:
                        if fname.endswith(ending) and not fname2 in res:
                            res.append(fname2)
    res.sort()
    return res

res = list_files(mypaths, ['.i', '.b'])
for r in res:
    uncompress_i(r, True)

