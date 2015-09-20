# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 22:28:41 2014

@author: marcus
"""

from subprocess import check_output
from os.path import isfile, join
from numpy import fromfile, fromstring, uint16, uint32, dtype
from math import ceil
import sys

lh5_header = b'SPIS\x1aLH5'
lh5_bin = './lh5'
data1_valid = [15, 5000, 10000, 15000, 30000, 50000, 100000, 120000, 150000, 200000, 2000000, 4000000, 4300000, 5000000, 5100000, 6000000, 8000000, 8600000, 9000000, 4144300032]
b1_header = b'\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00'

for lh5_path in sys.path:
    if isfile(join(lh5_path, lh5_bin)):
        lh5_bin = join(lh5_path, lh5_bin)
        break
  
def find_terminated_string(s, pos, term=0):
    i = s.find(term, pos)
    return s[pos:i]

def assert_zero(s):
    assert set(s) == set([0]), s

def read_iz_header(f):
    result = dict()
    a = fromfile(f, dtype=uint16, count=1)[0]
    assert a == 2, a
    assert_zero(f.read(4))
    result['length'] = fromfile(f, dtype=uint32, count=1)[0]
    result['unknown'] = fromfile(f, dtype=uint32, count=1)[0]
    assert_zero(f.read(2))
    result['start_pos'] = f.tell()
    return result
    
def read_b1_data(f, pos, length, id1):
    f.seek(pos)
    last = fromfile(f, dtype=uint32, count=1)[0]
    res = [last]

    while len(res) < length:
        l1 = fromfile(f, dtype=uint16, count=1)[0]
        s = f.read(l1 - 2)
        n = 0
        while n < len(s):
            if s[n] == 0:
                last += fromstring(s[n + 1:n + 3], dtype=uint16)[0]
                n += 3
            elif s[n] == 255:
                last = fromstring(s[n + 1:n + 5], dtype=uint32)[0]
                n += 5
            else:
                last += s[n]
                n += 1
            res.append(last)
    assert len(res) == length, (len(res), length)
    id1.update(set(res))       

def read_i_header(f):
    header = {}
    assert_zero(f.read(2))
    header['entrys'] = fromfile(f, dtype=uint32, count=1)[0]
    header['data1'] = fromfile(f, dtype=uint32, count=1)[0]
    if header['data1'] == 0x10:
        header['entry_size'] = 1 #None
        header['fixed_length'] = False
    else:
        assert header['data1'] in data1_valid, header['data1']
        a16 = fromfile(f, dtype=uint32, count=1)[0]
        assert a16 == 0x16, hex(a16)
        header['entry_size'] = fromfile(f, dtype=uint16, count=1)[0]
        header['fixed_length'] = True

    assert_zero(f.read(6))  

    header['start_pos'] = f.tell()
    f.seek(4, 1)
    s = f.read(len(lh5_header))
    header['compressed'] = s == lh5_header
    f.seek(header['start_pos'])
    return header
    
def read_lh5_header(f, pos=None):
    header = {}
    if pos:
        f.seek(pos)
    d = f.read(4)
    if d == b'':
        return None
    l = fromstring(d, dtype=uint32, count=1)[0]
    header['next_header'] = f.tell() + l
    b = f.read(len(lh5_header))
    assert b == lh5_header, (b'!' + b ,  hex(f.tell()))
    header['uncompressed_size'] = fromfile(f, dtype=uint32, count=1)[0]
    assert_zero(f.read(1))
    header['unknown']= fromfile(f, dtype=uint32, count=1)[0]
    assert_zero(f.read(4))
    header['compressed_start'] = f.tell()
    header['compressed_size'] = header['next_header'] - header['compressed_start']
    return header

def find_file(base_folder, sub_folders, file_name):
    for sub_folder in sub_folders:
        f1 = join(base_folder, sub_folder, file_name)
        if isfile(f1):
            return f1
    return None
    
from collections import OrderedDict

def parse_format(string, start, length, format_list):
    res = OrderedDict()
    pos = start
    if length != None:
        stop = start + length
    for f in format_list:
        if f['type'] in ['uint8', 'uint16', 'uint32']:
            t = dtype(f['type'])
            data = fromstring(string[pos:pos + t.itemsize], dtype=t, count=1)[0]
            pos += t.itemsize
        elif f['type'] == 'terminated_string':
            data = find_terminated_string(string, pos, ord(f['term_char']) if 'term_char' in f else 0)
            if not 'encode' in f or f['encode'] == True:
                data = data.decode('latin1')
            pos += len(data) + 1
        elif f['type'] == 'zeros' or f['type'] == 'fixed_string':
            if f['length'] == -1:
                assert pos < stop
                data = string[pos: stop]
            else:
                data = string[pos: pos + f['length']]
            if f['type'] == 'zeros':
                assert set(data) == set([0]), set(data)
            else:
                if 'encode' in f and f['encode'] == True:
                    data = data.decode('latin1')                
            pos += len(data)
        elif f['type'] == 'atend':
            data = ''
            assert pos == stop, (res, pos, stop,  data, length, f)
        else:
            print(res, f)
            assert False
        if length != None:
            assert pos <=stop, (res, pos, stop,  data, length, f)
        if 'expected' in f:
            assert data == f['expected'], (data, f['expected'])
        if 'name' in f:
            res[f['name']] = data
    assert pos <= stop
    return res
    
def open_read_i_entrys(entrys, i_file, iz_file, i_offset=0, iz_offset=0, format=[['d1','i04'],['d2','i04'],['name','s0d'],['personalnumber', 's00']]):
    f_i = open(i_file, 'rb')
    f_i.seek(i_offset)
    i_header = read_i_header(f_i)
    entrys = list(map(lambda x: x - 1, list(entrys)))
    entrys.sort()
    assert i_header['fixed_length']
    
    res = [None] * len(entrys)
    if i_header['compressed']:
        lh5_header = read_lh5_header(f_i)
        block_size =  lh5_header['uncompressed_size']
        f_iz = open(iz_file, 'rb')
        f_iz.seek(iz_offset)
        iz_header = read_iz_header(f_iz)
        f_iz.seek(iz_header['start_pos'])
        iz_indexes = fromfile(f_iz, count=iz_header['length'] * 4, dtype=uint32) + i_offset
        f_iz.close()        
        current_block_nr = None
    else:
        stop
        block = f_i.read()
        block_size = i_header['entry_size'] * i_header['entrys']
        assert block_size == len(block)
        current_block_nr = 0
    
    for n, entry in enumerate(entrys):
        assert entry < i_header['entrys']
        block_nr = (entry * i_header['entry_size']) / block_size
        if block_nr != current_block_nr:
            lh5_header = read_lh5_header(f_i, iz_indexes[block_nr])
            block = check_output([lh5_bin, i_file, str(lh5_header['uncompressed_size']), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
            current_block_nr = block_nr
        pos = (entry * i_header['entry_size']) % block_size
        pos_stop = pos + i_header['entry_size']
        res[n] = parse_format(block, pos, i_header['entry_size'], format)
    f_i.close()
    return res

def gen_block_index(f):
    res = []
    pos = f.tell()
    while pos != 0:
        f.seek(pos)        
        res.append(pos)
        lh5_header = read_lh5_header(f)
        if lh5_header:
            pos = lh5_header['next_header']
        else:
            pos = 0
    return res
 
def open_read_b_entrys(entrys, b_file, p_file, pz_file=None, b_offset=0, p_offset=0, pz_offset=0, format=[['d1','i04'],['d2','i04'],['name','s0d'],['personalnumber', 's00']]):
    f_b = open(b_file, 'rb')
    f_b.seek(b_offset)
    b_header = read_i_header(f_b)
    entrys = list(map(lambda x: x - 1, list(entrys)))
    entrys.sort()
    
    res = [None] * len(entrys)
    assert b_header['compressed']
    if pz_file:
        f_pz = open(pz_file, 'rb')
        f_pz.seek(pz_offset)
        pz_header = read_iz_header(f_pz)
        f_pz.seek(pz_header['start_pos'])
        index_block = fromfile(f_pz, count=pz_header['length'], dtype=uint32) + b_offset
    else:
        f_b.seek(b_header['start_pos'])
        index_block = gen_block_index(f_b)
    entrys_per_block = int(ceil(b_header['entrys'] / float(len(index_block))))
    assert entrys_per_block in [100, 300, 500], entrys_per_block       

    f_p = open(p_file, 'rb')
    f_p.seek(p_offset)
    p_header = read_iz_header(f_p) 

    last_block = -1
    for n, entry in enumerate(entrys):
        assert entry < b_header['entrys']
        block_nr = int(entry / entrys_per_block)
        if last_block != block_nr:
            lh5_header = read_lh5_header(f_b, index_block[block_nr])
            block = check_output([lh5_bin, b_file, str(lh5_header['uncompressed_size']), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
            last_block = block_nr

        f_p.seek(p_header['start_pos'] + 4 * entry)
        pos = fromfile(f_p, dtype=uint32, count=1)[0]
        a1 = fromstring(block[pos + 0:pos + 4], dtype=uint32)[0]
        a2 = fromstring(block[pos + 4:pos + 8], dtype=uint32)[0]
        f_p.seek(p_header['start_pos'] + 4 * (entry + 1))
        stop = fromfile(f_p, dtype=uint32, count=1)[0]
        if stop <= pos or entry == b_header['entrys'] - 1:
            stop = len(block)
        #nr = (pos + a2 - a1) / 12
        #assert (pos + a2 - a1) % 12 == 0
        #assert nr == entry, (nr, entry)
       
        assert  stop - pos - 12 == a2  
        res[n] = parse_format(block, pos + 8, stop - pos - 8, format)
 
    f_b.close()
    return res
