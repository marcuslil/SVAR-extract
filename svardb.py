# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 11:54:15 2015

@author: marcus
"""

from os.path import join, isfile
from svarfile import *
from svarsearch import *


class SVAR_db:
    files = None
    local_base_folder = None
    short_data_format = None
    detailed_data_format = None
        
    def search_data_reg(self, reg, search_terms, separator=';', accept_multiple=False):
        res = self.local_files[reg].search(separator.join(search_terms) + separator, Match_begin, return_type=SVAR_search_return.key)
        if accept_multiple:
            assert len(res) > 0, (res, search_terms, type(search_terms[0]))
        else:
            assert len(res) == 1, (res, search_terms, type(search_terms[0]))
        res = list(res)[0].split(separator)
        return res
        
    def set_backend_local_files(self, root='C:\\', base_folder=None):
        if not base_folder:
            base_folder = self.local_base_folder
        self.local_files = {}
        self.find_files(join(root, base_folder))

    def find_files(self, base_folder):
        for name, data in self.files.items():
            self.local_files[name] = {}
            file_name = data['file_name']
            if file_name.endswith('.i'):
                suffixes = {'base_file':'i', 'block_index':'iz', 'b1_file':'b1'}
            else:
                assert file_name.endswith('.b')
                suffixes = {'base_file':'b', 'block_index':'pz', 'entry_index':'p'}
    
    
            files = {}            
            for file_type, suffix in suffixes.items():
                files[file_type] = None
                for sub_folder in self.local_sub_folders:
                    f1 = join(base_folder, sub_folder, file_name[:-2] + '.' + suffix)
                    if isfile(f1):
                        files[file_type] = f1
                        break
            
            if data['type'] in ['short_data', 'detailed_data']:
                self.local_files[name] = SVAR_file(data_file_name=files['base_file'],
                                                  block_index_file_name=files['block_index'],
                                                  entry_index_file_name=files['entry_index'] if 'entry_index' in files else None)
            else:
                ignore_accents = 'local_file_ignore_accents' in data and data['local_file_ignore_accents']
                #if data['type'] == 'index':
                #    assert files['b1_file'] != None, data
                key_term_char = data['local_file_key_term_char'] if  'local_file_key_term_char' in data else '\x00'
                unique_keys = data['local_file_unique_keys'] if  'local_file_unique_keys' in data else True
                self.local_files[name] = SVAR_search(data_file_name=files['base_file'],
                                                    block_index_file_name=files['block_index'],
                                                    b1_file_name=files['b1_file'],
                                                    ignore_accents=ignore_accents,
                                                    key_term_char=key_term_char,
                                                    unique_keys=unique_keys)
            self.local_files[name].open()
            
    def search(self, search_terms=None, max_count=None):
        search_terms2 = dict(search_terms)
        short_data_id = None
        for search_field, search_words in search_terms.items():
            if search_field in self.files and self.files[search_field]['type'] == 'index':
                search_terms2.pop(search_field)
                if type(search_words) != list:
                    search_words = [search_words]
                match = Match_star if not search_field + '_match' in search_terms2 else search_terms2.pop(search_field + '_match')
                for search_word in search_words:
                    tmp = self.local_files[search_field].search(search_word, match, return_type=SVAR_search_return.short_index)
                    if short_data_id == None:
                        short_data_id = tmp
                    else:
                        short_data_id.intersection_update(tmp)

        assert not search_terms2, search_terms2
            
        short_data_id = list(short_data_id)
        short_data_id.sort()
        if not max_count in [0, None]:
            short_data_id = short_data_id[:max_count]
    
        return short_data_id
       
        
    def search_and_parse(self, search_terms=None, output='detailed_data', max_count=None):
        assert output in ['short_data_index', 'short_data', 'short_text', 'detailed_data_index', 'detailed_data', 'detailed_text'] or output.startswith('detailed_text_with_same_'), output
        
        res = self.search(search_terms, max_count)
                
        if output == 'short_data_index':
            return res

        res = [self.local_files['short_data'].read_entry(x - 1) for x in res]
        res = [parse_format(x, self.short_data_format) for x in res]
        if output == 'short_data':
            return res
                
        if output == 'short_text':
            return [self.format_short(x) for x in res]
    
        res = [x['detailed_data_id'] for x in res]
        res.sort()
        
        if output == 'detailed_data_index':
            return res
            
        res = [self.local_files['detailed_data'].read_entry(x - 1) for x in res]
        
        res = [parse_format(x, self.detailed_data_format) for x in res]

        if len(res) > 0 and 'id2' in res[0]:
            res_id2 = list(map(lambda x: int(x['id2']), res))
            assert set(res_id2) == set(id2), (res_id2, id2)
            
        if output == 'detailed_data':
            return res
                
        details = [self.format_details(x) for x in res]
        
        if output == 'detailed_text':
            return details
        elif output.startswith('detailed_text_with_same_'):
            return [detail + self.find_same(output[24:], data, 'short_text') for detail, data in zip(details, res)]

        raise Exception(output)
        
    def verify_sorted(self):
        for name, f in self.local_files.items():
            if type(f) == SVAR_search:
                print(name)
                if not f.verify_order():
                    print(name)
                    raise