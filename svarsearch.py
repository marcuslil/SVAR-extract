# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 23:09:31 2015

@author: marcus
"""

from svarfile import *
from numpy import uint16

[Match_exact, Match_any, Match_begin, Match_end, Match_star] = range(5)
b1_header = b'\x00\x00\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00'

from compare import *

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

class SVAR_search(SVAR_file):
    def __init__(self, data_file_name, block_index_file_name=None, b1_file_name=None):
        SVAR_file.__init__(self, data_file_name=data_file_name, block_index_file_name=block_index_file_name, file_type=File_type.fixed_size, entry_index_file_name=None)
        self.b1_file_name = b1_file_name
        
    def open(self):
        SVAR_file.open(self)
        if self.b1_file_name:
            self.b1_file = open(self.b1_file_name, 'rb')
            data = self.b1_file.read(16)
            assert data == b1_header
            
    def verify_order(self):
        self.load_block(0)
        entry = self.read_entry()
        last = find_terminated_string(entry, 8)
        while True:
            entry = self.read_entry()
            if not entry:
                return True
            data = find_terminated_string(entry, 8)
            comp = compare(last, data)
            print(last, data)
            if comp != -1:
                return False
            last = data
    
    def search(self, search_term, match=Match_star, output='b1', file_ignore_accents=False):
        if match == Match_star:
            if search_term.startswith('*') and search_term.endswith('*'):
                search_term = search_term[1:-1]
                match = Match_any
            elif search_term.endswith('*'):
                search_term = search_term[:-1]
                match = Match_begin
            elif search_term.startswith('*'):
                search_term = search_term[1:]
                match = Match_end
            else:
                match = Match_exact
                
        search_term = search_term.encode('latin1')
        search_term_length = len(search_term)
    
        if self.compressed:
            #find first and last block if compressed
            first_block_nr = 0
            last_block_nr = self.block_index_header['length']
            if match == Match_exact or match == Match_begin:
                while last_block_nr != first_block_nr + 1: # find_first index
                    test_block_nr = int((last_block_nr + first_block_nr) / 2)
                    self.load_block(test_block_nr, 1)     
                    entry = self.read_entry()
                    data = find_terminated_string(entry, 8)
                    comp = compare(data, search_term, ignore_accents=file_ignore_accents)
                    if comp < 0: # data before search_term
                        first_block_nr = test_block_nr
                    elif comp > 0 or file_ignore_accents:
                        last_block_nr = test_block_nr
                    else: #comp == 0:
                        first_block_nr = test_block_nr
                        last_block_nr = test_block_nr + 1
    
                if match == Match_begin or file_ignore_accents: # find last_block_nr
                    first_block_nr2 = first_block_nr
                    last_block_nr = self.block_index_header['length']
                    while last_block_nr != first_block_nr2 + 1:
                        test_block_nr = int((last_block_nr + first_block_nr2) / 2)
                        self.load_block(test_block_nr, 1)     
                        entry = self.read_entry()
                        data = find_terminated_string(entry, 8)
                        comp = compare(data[:search_term_length], search_term, file_ignore_accents)
                        if comp <= 0:
                            first_block_nr2 = test_block_nr
                        else:
                            last_block_nr = test_block_nr
        else:
            first_block_nr = 0
            last_block_nr = 1
        
        if match == Match_exact or match == Match_begin:
            self.load_block(first_block_nr)
            first_entry_nr = self.entrys_per_block * first_block_nr
            last_entry_nr = first_entry_nr + self.block_entrys
            while last_entry_nr != first_entry_nr + 1:
                test_entry_nr = int((first_entry_nr + last_entry_nr) / 2)
                entry = self.read_entry(test_entry_nr)
                a = fromstring(entry[0:8], uint32)
                assert a[0] == 0x00 and (a[1] == 0x90 or output != 'b1'), entry
                data = find_terminated_string(entry, 8)
                comp = compare(data, search_term, ignore_accents=file_ignore_accents)
                if comp < 0:
                    first_entry_nr = test_entry_nr
                elif comp > 0 or file_ignore_accents:
                    last_entry_nr = test_entry_nr
                else: # comp == 0:
                    first_entry_nr = test_entry_nr
                    last_entry_nr = test_entry_nr + 1

            if match == Match_begin or file_ignore_accents:
                if last_block_nr - 1 != self.curr_block_nr:
                    self.load_block(last_block_nr - 1)
                first_entry_nr2 = self.entrys_per_block * (last_block_nr - 1)
                last_entry_nr = first_entry_nr2 + self.block_entrys
                while last_entry_nr != first_entry_nr2 + 1:
                    test_entry_nr = int((first_entry_nr2 + last_entry_nr) / 2)
                    entry = self.read_entry(test_entry_nr)
                    data = find_terminated_string(entry, 8)
                    comp = compare(data[:search_term_length], search_term, file_ignore_accents)
                    if comp <= 0:
                        first_entry_nr2 = test_entry_nr
                    else:
                        last_entry_nr = test_entry_nr
        else:
            first_entry_nr = 0
            last_entry_nr = self.nr_entrys

        result = set()
        
        for entry_nr in range(first_entry_nr, last_entry_nr):
            entry = self.read_entry(entry_nr)
            a = fromstring(entry[0:8], uint32)
            assert a[0] == 0x00 and (a[1] == 0x90 or output != 'b1'), entry
            data = find_terminated_string(entry, 8)
            if (match == Match_exact and compare(data, search_term, file_ignore_accents) == 0) or \
               (match == Match_begin and compare(data[:search_term_length], search_term, file_ignore_accents) == 0) or \
               (match == Match_end   and compare(data[-search_term_length:-1],  search_term) == 0) or \
               (match == Match_any   and data.find(search_term) != -1):

                if output=='b1':
                    n = len(data) + 9
                    b1_pos, b1_len = fromstring(entry[n:n + 8], dtype=uint32, count=2)
                    if b1_len == 0:
                        result.add(b1_pos)
                    else:
                        read_b1_data(self.b1_file, b1_pos, b1_len, result)
                else:
                    result.add(data.decode('latin1'))
        return result