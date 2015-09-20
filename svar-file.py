# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 23:43:25 2015

@author: marcus
"""

from common import *
import io
from enum import Enum
import struct

class SVAR_file:
    
    class File_type(Enum):
        fixed_size = 0
        variable_size = 1
    
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
        
        self.data_file = None
        self.block_index_file = None
        self.curr_block = io.BytesIO(b'')
        self.curr_block_nr = -1
        
    def open_iz_file(self):
        if self.block_index_file == None:
            self.block_index_file = open(self.block_index_file_name, 'rb')
            self.iz_header = read_iz_header(self.block_index_file)
            self.block_index_file.seek(self.iz_header['start_pos'])
            self.index_block = fromfile(self.block_index_file, count=self.iz_header['length'], dtype=uint32)
            
    def open_entry_index_file(self):
        self.entry_index_file = open(self.entry_index_file_name, 'rb')
        self.entry_index_header = read_iz_header(self.entry_index_file)
            
    def open_data_file(self):
        if self.data_file == None:
            self.data_file = open(self.data_file_name, 'rb')
            # guess file type
            if self.file_type == None:
                self.data_file.seek(6)
                tmp = struct.unpack('I', self.data_file.read(4))[0]
                if tmp == 0x10:
                    self.file_type = self.File_type.variable_size
                else:
                    self.file_type = self.File_type.fixed_size
                self.data_file.seek(0)

            # read header
            assert self.data_file.read(2) == bytes(2)
            self.nr_entrys = struct.unpack('I', self.data_file.read(4))[0]
            if self.file_type == self.File_type.fixed_size:
                self.unknown1, self.data_offset, self.entry_size = struct.unpack("<IIH", self.data_file.read(10))
            else:
                self.data_offset = struct.unpack("I", self.data_file.read(4))[0]
            assert self.data_file.read(6) == bytes(6)
            assert self.data_file.tell() == self.data_offset, (self.data_file.tell(), self.data_offset)
            
            # check if compressed
            self.data_file.seek(4, 1)
            s = self.data_file.read(len(lh5_header))
            self.compressed = s == lh5_header
            if self.compressed and self.file_type == self.File_type.fixed_size:
                self.data_file.seek(self.data_offset)
                self.first_lh5_header = read_lh5_header(self.data_file)
                assert self.first_lh5_header['uncompressed_size'] % self.entry_size == 0
                self.entrys_per_block = int(self.first_lh5_header['uncompressed_size'] / self.entry_size)
            self.data_file.seek(self.data_offset)
            
            
            if self.file_type == self.File_type.fixed_size:
                assert self.entry_index_file_name == None
            else:
                assert self.entry_index_file_name != None
                self.open_entry_index_file()
                self.open_iz_file()
                self.entrys_per_block = int(ceil(self.nr_entrys / float(self.iz_header['length'])))                
                assert self.entrys_per_block in [100, 300, 500], entrys_per_block

            
    def load_block(self, block_nr=-1, nr_entries=-1):
        self.open_data_file()
        if self.compressed == True:
            if block_nr == -1: # next block
                self.curr_block_nr += 1
            else:
                self.open_iz_file()
                self.data_file.seek(self.index_block[block_nr])
                self.curr_block_nr = block_nr

            lh5_header = read_lh5_header(self.data_file)
            
            if self.file_type == self.File_type.fixed_size:
                assert lh5_header['uncompressed_size'] <= self.first_lh5_header['uncompressed_size']
                
            size = lh5_header['uncompressed_size'] if nr_entries == -1 else min(self.entry_size * nr_entries, lh5_header['uncompressed_size'])            
            data = check_output([lh5_bin, self.data_file_name, str(size), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
            self.curr_block = io.BytesIO(data)
            self.data_file.seek(lh5_header['next_header'])
        else:
            assert block_nr in [-1, 0]
            self.curr_block = self.data_file
    
    def goto(self, entry_nr):    
        if self.compressed:
            block_nr = int(entry_nr / self.entrys_per_block)
            if block_nr != self.curr_block_nr:
                self.load_block(block_nr)
            sub_entry = entry_nr % self.entrys_per_block
            if self.file_type == self.File_type.fixed_size:
                self.curr_block.seek(sub_entry * self.entry_size)
            else:
                self.entry_index_file.seek(self.entry_index_header['start_pos'] + entry_nr * 4)
                pos = struct.unpack('I', self.entry_index_file.read(4))[0]
                self.curr_block.seek(pos)
        else:
            self.curr_block.seek(entry_nr * self.entry_size + self.data_offset)
        
    def read_entry(self, entry_nr=-1):
        self.open_data_file()
        if entry_nr != -1:
            self.goto(entry_nr)

        read_size = 12 if self.file_type == self.File_type.variable_size else self.entry_size            
        res = self.curr_block.read(read_size)
        if not res:
            self.load_block()
            res = self.curr_block.read(read_size)
        
        if self.file_type == self.File_type.fixed_size:
            return res
        else:
            (unknown, length, zero) = struct.unpack("3I", res)
            assert zero == 0

            res = self.curr_block.read(length)
            return res
            
            
s1 = SVAR_file('/sharedwine/default/drive_c/SVBEF1990/hdbas/svbef1990reg2.i')
#for a in range(156640* 0 + 2000):
#    s1.read_entry(-1)
s1.read_entry()



#s2 = SVAR_file('/sharedwine/default/drive_c/SVBEF1990/hdbas/svbef1990reg7.i')
#print(s2.read_entry())

s3 = SVAR_file(data_file_name='/sharedwine/default/drive_c/SVBEF1990/hdbas/svbef1990reg.b', entry_index_file_name='/sharedwine/default/drive_c/SVBEF1990/hdbas/svbef1990reg.p')
for a in range(1):
    s3.read_entry()
