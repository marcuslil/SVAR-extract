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
from enum import Enum   

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
   
class SVAR_search_return(Enum):
    raw = 0
    key = 1
    data = 2
    short_index = 3
    index = 4

class SVAR_search(SVAR_file):
    def __init__(self, data_file_name, block_index_file_name=None, b1_file_name=None, ignore_accents=False, key_term_char = b'\x00', unique_keys=True):
        SVAR_file.__init__(self, data_file_name=data_file_name, block_index_file_name=block_index_file_name, file_type=File_type.fixed_size, entry_index_file_name=None)
        self.b1_file_name = b1_file_name
        self.ignore_accents = ignore_accents
        self.key_term_char = ord(key_term_char)
        self.unique_keys = unique_keys
        
    def open(self):
        SVAR_file.open(self)
        if self.b1_file_name:
            self.b1_file = open(self.b1_file_name, 'rb')
            data = self.b1_file.read(16)
            assert data == b1_header
            
    def verify_order(self):
        self.load_block(0)
        entry = self.read_entry()
        last = self.parse_key(entry)
        n = 0
        status = True
        while True:
            entry = self.read_entry()
            if not entry:
                return status
            key = self.parse_key(entry)
            comp = compare(last, key, self.ignore_accents)
            if comp == 1 or (comp == 0 and self.ignore_accents == False and self.unique_keys == True):
                print(n, '\n', last.decode('latin1'), '\n', key.decode('latin1'), comp)
                status = False
            last = key
            n += 1

    def parse_key(self, entry):
        pos = entry.find(self.key_term_char, 8)
        return entry[8:pos]
    
    def search(self, search_term, match=Match_star, return_type=SVAR_search_return.key):
        assert isinstance(return_type, SVAR_search_return)
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
        
        non_uniqe_keys = self.ignore_accents or self.unique_keys == False
    
        if self.compressed:
            #find first and last block if compressed
            first_block_nr = 0
            last_block_nr = self.block_index_header['length']
            if match == Match_exact or match == Match_begin:
                while last_block_nr != first_block_nr + 1: # find_first index
                    test_block_nr = int((last_block_nr + first_block_nr) / 2)
                    self.load_block(test_block_nr, 1)     
                    entry = self.read_entry()
                    key = self.parse_key(entry)
                    comp = compare(key, search_term, ignore_accents=self.ignore_accents)
                    if comp < 0: # data before search_term
                        first_block_nr = test_block_nr
                    elif comp > 0 or non_uniqe_keys:
                        last_block_nr = test_block_nr
                    else: #comp == 0:
                        first_block_nr = test_block_nr
                        last_block_nr = test_block_nr + 1
    
                if match == Match_begin or non_uniqe_keys: # find last_block_nr
                    first_block_nr2 = first_block_nr
                    last_block_nr = self.block_index_header['length']
                    while last_block_nr != first_block_nr2 + 1:
                        test_block_nr = int((last_block_nr + first_block_nr2) / 2)
                        self.load_block(test_block_nr, 1)     
                        entry = self.read_entry()
                        key = self.parse_key(entry)
                        comp = compare(key[:search_term_length], search_term, self.ignore_accents)
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
                key = self.parse_key(entry)
                comp = compare(key, search_term, ignore_accents=self.ignore_accents)
                if comp < 0:
                    first_entry_nr = test_entry_nr
                elif comp > 0 or non_uniqe_keys:
                    last_entry_nr = test_entry_nr
                else: # comp == 0:
                    first_entry_nr = test_entry_nr
                    last_entry_nr = test_entry_nr + 1

            if match == Match_begin or non_uniqe_keys:
                self.load_block(last_block_nr - 1)
                first_entry_nr2 = self.entrys_per_block * (last_block_nr - 1)
                last_entry_nr = first_entry_nr2 + self.block_entrys
                while last_entry_nr != first_entry_nr2 + 1:
                    test_entry_nr = int((first_entry_nr2 + last_entry_nr) / 2)
                    entry = self.read_entry(test_entry_nr)
                    key = self.parse_key(entry)
                    comp = compare(key[:search_term_length], search_term, self.ignore_accents)
                    if comp <= 0:
                        first_entry_nr2 = test_entry_nr
                    else:
                        last_entry_nr = test_entry_nr
        else:
            first_entry_nr = 0
            last_entry_nr = self.nr_entrys

        if return_type == SVAR_search_return.short_index:
            result = set()
        else:
            result = list()
        hits = 0
        
        for entry_nr in range(first_entry_nr, last_entry_nr):
            entry = self.read_entry(entry_nr)
            a = fromstring(entry[0:8], uint32)
            #assert a[1] == 0x90 or output != 'b1', entry
            key = self.parse_key(entry)
            if (match == Match_exact and compare(key, search_term) == 0) or \
               (match == Match_begin and compare(key[:search_term_length], search_term) == 0) or \
               (match == Match_end   and compare(key[-search_term_length:], search_term) == 0) or \
               (match == Match_any   and key.find(search_term) != -1): #wont ignore case
                hits += 1

                if return_type==SVAR_search_return.short_index:
                    if a[0] == 0:
                        n = len(key) + 9
                        b1_pos, b1_len = fromstring(entry[n:n + 8], dtype=uint32, count=2)
                        if b1_len == 0:
                            result.add(b1_pos)
                        else:
                            read_b1_data(self.b1_file, b1_pos, b1_len, result)
                    else:
                        result.add(a[0])
                elif return_type==SVAR_search_return.index:
                    result.append(entry_nr)
                elif return_type==SVAR_search_return.key:
                    result.append(key.decode('latin1'))
                elif return_type==SVAR_search_return.data:
                    n = len(key) + 9
                    data = find_terminated_string(entry, n)
                    result.append(data.decode('latin1'))
                else:
                    raise
                    
        if match == Match_exact and self.unique_keys:
            assert hits <= 1, hits
        return result