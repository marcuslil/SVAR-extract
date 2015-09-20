# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:18:49 2015

@author: marcus
"""

from common import *
from copy import deepcopy
from compare import compare
from numpy import fromstring

[Match_exact, Match_exact_ignore_accents, Match_any, Match_begin, Match_end, Match_star] = range(6)
   
def find_files(setup):
    sub_folders = setup['sub_folders'] if 'sub_folders' in setup else ['cdbas', 'hdbas']
    for key, f in setup['files'].items():
        setup['files'][key] = {}
        if f.endswith('.i'):
            suffixes = ['i', 'iz', 'b1']
        else:
            assert f.endswith('.p')
            suffixes = ['b', 'pz', 'p']
        for suffix in suffixes:
            filename = find_file(setup['base_folder'], sub_folders, f[:-2] + '.' + suffix)
            if filename:
                setup['files'][key][suffix + '_file'] = filename

def search_indexed_file(search_term, i_file, iz_file=None, b1_file=None, match=Match_star, output='b1', file_ignore_accents=False):
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

    if match == Match_exact_ignore_accents:
        file_ignore_accents = True
    if match == Match_any:
        search_term_unicode = search_term.decode('latin1').lower()
    ids = set()
    f_i = open(i_file, 'rb')
    i_header = read_i_header(f_i)
    l = len(search_term)
    if i_header['compressed']:
        f_iz = open(iz_file, 'rb')
        iz_header = read_iz_header(f_iz)
        f_iz.seek(iz_header['start_pos'])
        iz_indexes = fromfile(f_iz, count=iz_header['length'] * 4, dtype=uint32)
        f_iz.close()
        #assert header['data1'] * 10 == index['unknown'], (header['data1'], index['unknown'])
        # find first and last index if searching sorted
        first_index = 0
        last_index = iz_header['length']
        if match == Match_exact or match == Match_begin or match==Match_exact_ignore_accents:
            while last_index != first_index + 1: # find_first index
                test_index = int((last_index + first_index) / 2)
                lh5_header = read_lh5_header(f_i, iz_indexes[test_index])
                s = check_output([lh5_bin, i_file, str(i_header['entry_size']), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
                data = find_terminated_string(s, 8)
                comp = compare(data, search_term, ignore_accents=file_ignore_accents)
                if comp < 0: # data before search_term
                    first_index = test_index
                elif comp > 0 or file_ignore_accents:
                    last_index = test_index
                else: #comp == 0:
                    first_index = test_index
                    last_index = test_index + 1

            if match == Match_begin or file_ignore_accents: # find last_index
                first_index2 = first_index
                last_index = iz_header['length']
                while last_index != first_index2 + 1:
                    test_index = int((last_index + first_index2) / 2)
                    lh5_header = read_lh5_header(f_i, iz_indexes[test_index])
                    s = check_output([lh5_bin, i_file, str(i_header['entry_size']), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
                    data = find_terminated_string(s, 8)
                    comp = compare(data[:l], search_term, file_ignore_accents)
                    if comp <= 0:
                        first_index2 = test_index
                    else:
                        last_index = test_index
    else:
        first_index = 0
        last_index = 1
        
    if output=='b1':
        f_b1 = open(b1_file, 'rb')
        data = f_b1.read(16)
        assert data == b1_header, map(ord, data)
    
    for index_n in range(first_index, last_index):
        if i_header['compressed']:
            lh5_header = read_lh5_header(f_i, iz_indexes[index_n])
            block = check_output([lh5_bin, i_file, str(lh5_header['uncompressed_size']), str(lh5_header['compressed_start']), str(lh5_header['compressed_size'])])
        else:
            block = f_i.read(i_header['entrys'] * i_header['entry_size'])
            
        first_entry = 0
        if index_n == first_index and (match == Match_exact or match == Match_begin or match == Match_exact_ignore_accents):
            last_entry = len(block) / i_header['entry_size']
            while last_entry != first_entry + 1:
                test_entry = int((first_entry + last_entry) / 2)
                n = test_entry * i_header['entry_size']     
                assert fromstring(block[n + 0: n + 4], dtype=uint32, count=1)[0] == 0x00, (hex(n), ord(block[n+5]))
                if output=='b1':
                    assert fromstring(block[n + 4: n + 8], dtype=uint32, count=1)[0] == 0x90, (hex(n), ord(block[n+5]))
                n += 8
                data = find_terminated_string(block, n)
                comp = compare(data, search_term, ignore_accents=file_ignore_accents)
                if comp < 0:
                    first_entry = test_entry
                elif comp > 0 or file_ignore_accents:
                    last_entry = test_entry
                else: # comp == 0:
                    first_entry = test_entry
                    last_entry = test_entry + 1
            
        for n in range(first_entry * i_header['entry_size'], len(block), i_header['entry_size']):
            assert fromstring(block[n + 0: n + 4], dtype=uint32, count=1)[0] == 0x00, (hex(n), ord(block[n+5]))
            if output=='b1':
                assert fromstring(block[n + 4: n + 8], dtype=uint32, count=1)[0] == 0x90, (hex(n), ord(block[n+5]))
            n += 8
            data = find_terminated_string(block, n)
            l = min(len(search_term), len(data))
            n += len(data) + 1
            if match == Match_any:
                data_unicode = data.decode('latin1').lower()
            if (match == Match_exact and compare(data, search_term) == 0) or \
               (match == Match_exact_ignore_accents and compare(data, search_term, True) == 0) or \
               (match == Match_begin and compare(data[:len(search_term)], search_term) == 0) or \
               (match == Match_end and compare(data[-len(search_term):], search_term) == 0) or \
               (match == Match_any and data_unicode.count(search_term_unicode) > 0):

                if output=='b1':
                    b1_pos = fromstring(block[n + 0: n + 4], dtype=uint32, count=1)[0]
                    b1_len = fromstring(block[n + 4: n + 8], dtype=uint32, count=1)[0]
                    if b1_len == 0:
                        ids.add(b1_pos)
                    else:
                        read_b1_data(f_b1, b1_pos, b1_len, ids)
                    '''
                    for n in range(n + 8, n_stop):
                        assert ord(block[n]) == 0, ord(block[n])'''
                else:
                    ids.add(data.decode('latin1'))
                if match == Match_exact:
                    break
            elif match == Match_begin and len(ids) > 0:
                break
    f_i.close()
    if output=='b1':
        f_b1.close()
    return ids

def search_setup(setup, searches=None):
    searches = deepcopy(searches)

    id1_list = None
    for search_field in setup['search_fields']:
        if search_field in searches:
            search_terms = searches.pop(search_field)
            if type(search_terms) != list:
                search_terms = [search_terms]
            match = Match_star if not search_field + '_match' in searches else searches.pop(search_field + '_match')
            for search_term in search_terms:
                args = dict([('search_term', search_term), ('match', match)] | setup['files'][search_field + '_index'].items())
                tmp = search_indexed_file(**args)
                if id1_list == None:
                    id1_list = tmp
                else:
                    id1_list.intersection_update(tmp)
    assert searches == {}, searches
        
    id1_list = list(id1_list)
    id1_list.sort()

    return id1_list

def search_and_parse_setup(setup, searches=None, id1_list=None, output='id1_list', max_count=None):
    assert output in ['id1_list', 'brief_data', 'brief_text', 'id2_list', 'detailed_data', 'detailed_text', 'detailed_text_with_same_address', 'detailed_text_with_same_address_and_last_name', 'detailed_text_with_same_estate', 'detailed_text_with_same_estate_and_last_name'], output
    
    id1_list = search_setup(setup, searches)

    if not max_count in [0, None]:
        id1_list = id1_list[:max_count]

    if output == 'id1_list':
        return id1_list

    res = open_read_i_entrys(**dict([['entrys', id1_list], ['format', setup['id1_format']]] + list(setup['files']['id1'].items())))
    if output == 'brief_data':
        return res
    
    if output == 'brief_text':
        return map(setup['get_short'], res)

    id2 = list(map(lambda x: x['id2'], res))
    if output == 'id2_list':
        return id2

    args = dict([['entrys', id2], ['format', setup['id2_format']]] + list(setup['files']['id2'].items()))
    res = open_read_b_entrys(**args)
    if len(res) > 0 and 'id2' in res[0]:
        res_id2 = list(map(lambda x: int(x['id2']), res))
        assert set(res_id2) == set(id2), (res_id2, id2)
        
    if output == 'detailed_data':
        return res
            
    return [setup['get_details'](r, output=output) for r in res]

