# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 19:33:59 2014

@author: marcus

Test if compare algorithm is ok

"""
from common import *
from common_search import *
import compare
import setup_sveriges_befolkning_1970, setup_sveriges_befolkning_1980, setup_sveriges_befolkning_1990, setup_sveriges_dodbok_2009, setup_sveriges_befolkning_1890, setup_sveriges_befolkning_1900

    
def test_compare(fname, compare = compare.compare, ignore_accents=False, equal_ok=False):
    f = open(fname, 'rb')
    header = read_i_header(f)
    if not header['fixed_length']:
        return
    last = None
    entrys = 0
    
    while entrys < header['entrys']:
        if header['compressed']:
            lh5_header = read_lh5_header(f)
            if not lh5_header:
                break
            s = check_output([lh5_bin, fname, str(lh5_header['uncompressed_size']), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
        else:
            s = f.read(header['entry_size']) # * header['entrys'])
            if len(s) == 0:
                break

        for n in range(0, len(s), header['entry_size']):
            current = find_terminated_string(s, n + 8)
            if last:
                #print '!' + last.decode('latin1') + '!' ,  '!' + current.decode('latin1') + '!'
                comp = compare(last, current, ignore_accents=ignore_accents)
                if comp == 0 and (ignore_accents or equal_ok):
                    pass
                elif comp != -1:
                    if not (compare(last, current) == 0 and comp == 0):
                        print('1:' + last.decode('latin1') + '<') #, map(hex, map(ord, last))
                        print('2:' + current.decode('latin1') + '<') #, map(hex, map(ord, current))
                        #return
            last = current
            entrys += 1
            #if entrys > 500000:
            #    f.close()
            #    return
        if header['compressed']:
            f.seek(lh5_header['next_header'])
    f.close()




#/sharedwine/default/drive_c/SVBEF70/cdbas/ma70re12.i
#1:26600;Råå;Lübecksg 20<
#2:26600;Råå;Lybecksg 21<

setups = [setup_sveriges_befolkning_1970.setup,
          setup_sveriges_befolkning_1980.setup,
          setup_sveriges_befolkning_1990.setup,
          setup_sveriges_dodbok_2009.setup,
          setup_sveriges_befolkning_1890.setup,
          setup_sveriges_befolkning_1900.setup]


for setup in setups:
    for f in setup['files'].values():
        if 'i_file' in f:
            equal_ok =  f['i_file'].endswith('be1890.i') or f['i_file'].endswith('be1900.i') 
            print(f['i_file'])
            ignore_accents = 'file_ignore_accents' in f and f['file_ignore_accents']
            test_compare(f['i_file'], ignore_accents=ignore_accents, equal_ok=equal_ok)
