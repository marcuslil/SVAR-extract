# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 23:43:25 2015

@author: marcus
"""

import io
from enum import Enum
from numpy import fromfile, fromstring, uint32, dtype
from subprocess import check_output
from collections import OrderedDict
from os.path import isfile, join
from sys import path
from math import ceil

lh5_header = b'SPIS\x1aLH5'
lh5_bin = './lh5'
data1_valid = [15, 5000, 10000, 15000, 30000, 50000, 100000, 120000, 150000, 200000, 2000000, 4000000, 4300000, 5000000, 5100000, 6000000, 8000000, 8600000, 9000000, 4144300032]
lh5_dtype = dtype('u4, S8, u4, u1, u4, u4')
iz_dtype = dtype('u2, u4, u4, u4, u2')

for lh5_path in path:
    if isfile(join(lh5_path, lh5_bin)):
        lh5_bin = join(lh5_path, lh5_bin)
        break

def find_terminated_string(s, pos, term=0):
    i = s.find(term, pos)
    return s[pos:i]

class File_type(Enum):
    fixed_size = 0
    variable_size = 1

def parse_format(string, format_list):
    res = OrderedDict()
    pos = 0
    length = len(string)

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
                assert pos < length
                data = string[pos: length]
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
            assert pos == length, (res, pos, data, length, f)
        else:
            print(res, f)
            assert False
        if length != None:
            assert pos <= length, (res, pos, data, length, f)
        if 'expected' in f:
            assert data == f['expected'], (data, f['expected'])
        if 'name' in f:
            res[f['name']] = data
    assert pos <= length
    return res

def read_lh5_header(f):
    header = dict()
    pos = f.tell()
    data = fromfile(f, lh5_dtype, 1)
    if not data:
        return None
    data = data[0]
    header['next_header'] = pos + data[0] + 4
    assert data[1] == lh5_header, (b'!' + data[1] ,  hex(f.tell()))
    header['uncompressed_size'] = data[2]
    assert data[3] == 0
    header['unknown'] = data[4]
    assert data[5] == 0
    header['compressed_start'] = f.tell()
    header['compressed_size'] = header['next_header'] - header['compressed_start']
    return header

def read_iz_header(f):
    result = dict()
    data = fromfile(f, dtype=iz_dtype, count=1)[0]
    assert data[0] == 2, data
    assert data[1] == 0, data
    result['length'] = data[2]
    result['unknown'] = data[3]
    assert data[4] == 0, data
    result['start_pos'] = f.tell()
    return result

class SVAR_file:   
    def __init__(self, data_file_name, block_index_file_name=None, file_type=None, entry_index_file_name=None):
        self.data_file_name = data_file_name
        if not block_index_file_name:
            if data_file_name[-2:] == '.b':
                block_index_file_name = data_file_name[:-1] + 'pz'
            else:
                block_index_file_name = data_file_name + 'z'

        self.block_index_file_name = block_index_file_name
        self.entry_index_file_name = entry_index_file_name
        self.file_type = file_type
        
        self.is_open = False

    def open(self):
        assert self.is_open == False
        self.is_open = True
        
        #open data file
        self.data_file = open(self.data_file_name, 'rb')

        # guess file type
        if self.file_type == None:
            self.data_file.seek(6)
            tmp = fromfile(self.data_file, uint32, 1)[0]
            if tmp == 0x10:
                self.file_type = File_type.variable_size
            else:
                self.file_type = File_type.fixed_size
            self.data_file.seek(0)

        # read header
        assert self.data_file.read(2) == bytes(2)
        self.nr_entrys = fromfile(self.data_file, uint32, 1)[0]
        if self.file_type == File_type.fixed_size:
            self.unknown1, self.data_offset, self.entry_size = fromfile(self.data_file, "<u4, <u4, <u2", 1)[0]
            self.entry_size = int(self.entry_size)
        else:
            self.data_offset = fromfile(self.data_file, uint32, 1)[0]
        assert self.data_file.read(6) == bytes(6)
        assert self.data_file.tell() == self.data_offset, (self.data_file.tell(), self.data_offset)
        
        # check if compressed
        self.data_file.seek(4, 1)
        s = self.data_file.read(len(lh5_header))
        self.data_file.seek(self.data_offset)
        self.compressed = s == lh5_header
        
        # open block index file and read header
        if self.compressed:
            self.block_index_file = open(self.block_index_file_name, 'rb')
            self.block_index_header = read_iz_header(self.block_index_file)

        # open entry index file and read header
        if self.file_type == File_type.fixed_size:
            assert self.entry_index_file_name == None
        else:
            self.entry_index_file = open(self.entry_index_file_name, 'rb')
            self.entry_index_header = read_iz_header(self.entry_index_file)

        #find entrys per block
        if not self.compressed:
            self.entrys_per_block = self.nr_entrys
        else:
            if self.file_type == File_type.fixed_size:
                self.first_lh5_header = read_lh5_header(self.data_file)
                self.data_file.seek(self.data_offset)
                assert self.first_lh5_header['uncompressed_size'] % self.entry_size == 0
                self.entrys_per_block = int(self.first_lh5_header['uncompressed_size'] / self.entry_size)
            else:
                self.entrys_per_block = int(ceil(self.nr_entrys / float(self.block_index_header['length'])))                
                assert self.entrys_per_block in [100, 300, 500], self.entrys_per_block
        
        #empty buffer at start
        self.curr_block = io.BytesIO(b'')
        self.curr_block_nr = -1
        self.curr_block_size_loaded = 0
        if self.file_type == File_type.fixed_size:
            self.block_entrys = 0
    
    def load_block(self, block_nr=-1, nr_entries=-1):
        if self.compressed == True:
            if block_nr == -1: # next block
                block_nr = self.curr_block_nr + 1
            else:
                self.block_index_file.seek(block_nr * 4 + self.block_index_header['start_pos'])
                offset = fromfile(self.block_index_file, uint32, 1)[0]
                self.data_file.seek(offset)

            lh5_header = read_lh5_header(self.data_file)
            if not lh5_header:
                self.curr_block = io.BytesIO(b'')
                self.block_entrys = 0
                self.curr_block_size_loaded = 0
                return
            
            if self.file_type == File_type.fixed_size:
                assert lh5_header['uncompressed_size'] <= self.first_lh5_header['uncompressed_size']
                
            size = lh5_header['uncompressed_size'] if nr_entries == -1 else min(self.entry_size * nr_entries, lh5_header['uncompressed_size'])
            if size == self.curr_block_size_loaded and self.curr_block_nr == block_nr:
                self.curr_block.seek(0)
            else:
                data = check_output([lh5_bin, self.data_file_name, str(size), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
                assert len(data) == size
                self.curr_block = io.BytesIO(data)
                if self.file_type == File_type.fixed_size:
                    self.block_entrys = int(lh5_header['uncompressed_size'] / self.entry_size)
                self.curr_block_size_loaded = len(data)
                
            self.data_file.seek(lh5_header['next_header'])
        else:
            if block_nr == -1:
                block_nr = self.curr_block_nr + 1
            assert block_nr in [0, 1], block_nr
            self.curr_block = self.data_file
            if block_nr == 0:
                self.curr_block.seek(self.data_offset)
            else:
                self.curr_block.seek(0, 2)
            if self.file_type == File_type.fixed_size:
                self.block_entrys = self.nr_entrys

        self.curr_block_nr = block_nr
    
    def goto(self, entry_nr):    
        if self.compressed:
            block_nr = int(entry_nr / self.entrys_per_block)
            self.load_block(block_nr)
            sub_entry = entry_nr % self.entrys_per_block
            if self.file_type == File_type.fixed_size:
                self.curr_block.seek(sub_entry * self.entry_size)
            else:
                self.entry_index_file.seek(self.entry_index_header['start_pos'] + entry_nr * 4)
                pos = fromfile(self.entry_index_file, uint32, 1)[0]
                self.curr_block.seek(pos)
        else:
            self.curr_block.seek(entry_nr * self.entry_size + self.data_offset)
        
    def read_entry(self, entry_nr=-1):
        assert self.is_open == True
        if entry_nr != -1:
            self.goto(entry_nr)

        read_size = 8 if self.file_type == File_type.variable_size else self.entry_size            
        res = self.curr_block.read(read_size)
        if not res:
            self.load_block()
            res = self.curr_block.read(read_size)
        
        if self.file_type == File_type.fixed_size:
            return res
        else:
            (unknown, length) = fromstring(res, "<u4, <u4")[0]
            length = int(length)
            res = self.curr_block.read(length + 4)
            return res