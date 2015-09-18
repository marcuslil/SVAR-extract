# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:52:01 2015

@author: marcus
"""

from common_search import *

setup = {'base_folder': '/sharedwine/default/drive_c/SVBEF1890',
         'id1_file': 'be1890',
         'id1_format':
             [{'name': 'd1', 'type': 'uint32'},
              {'type': 'uint32', 'expected': 0x90},
              {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\xff'},
              {'name': 'year', 'type': 'terminated_string', 'term_char': '\xff'},
              {'name': 'member_nr', 'type': 'terminated_string', 'term_char': '\xff'},
              {'name': 'relation', 'type': 'terminated_string'}],
         'id2_format': [{'type': 'uint', 'length': 4, 'expected': 0},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown1', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown2', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown3', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown4', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown5', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown6', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown7', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown8', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'first_names', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'last_names', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown9', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown10', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown11', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown12', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown13', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown14', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown15', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown15', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown16', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown17', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown18', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown19', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown20', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown21', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown22', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 1}, {'name': 'unknown23', 'type': 'terminated_string'},
                        {'type': 'uint', 'length': 1, 'expected': 5}, {'name': 'unknown24', 'type': 'terminated_string'},
                        {'type': 'atend'}],
         'files': {'id1': 'be1890.i',
                   'id2': 'be1890.p',
                   'last_name_index': 'be1890s1.i',
                   'first_names': 'be1890s2.i'}
        }
find_files(setup)