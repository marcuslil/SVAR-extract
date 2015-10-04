# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:30:57 2015

@author: marcus
"""

from svardb import SVAR_db
from svarsearch import *

class sveriges_befolkning_1990(SVAR_db):
    def __init__(self):
        pass

    def format_short(self, r):
        return r['name'] + '\t' + r['birth_date'][:4] + '-' + r['birth_date'][4:6] + '-' + r['birth_date'][6:8]

    def format_details(self, r):
        details = u'' + r['personal_number'][:4] + '-' + r['personal_number'][4:6] + '-' + r['personal_number'][6:8] + '\n\n' + r['name'] + '\n'
        
        if r['address1'] == '' and r['address2'] == '':
            details = details + '\n(Inga adressuppgifter)\n'
        else:
            details = details + '\n' + r['address1'] + '\n' + r['address2'] + '\n'
    
        living = r['living'].split(';')
        assert len(living) == 4
        
        details = details + '\nMantalsskriven i ' +  living[2] + ' (' + living[1] + ', ' + living[0] + ', ' + living[3] + '), fastigheten ' + r['living_estate'] + '.\n'
    
        born = r['born'].split(';')
        assert len(born) == 2, born
        if born[1] == '[Utomlands]':
            details = details + '\nFödd ' + str(int(r['personal_number'][6:8])) + '/' + str(int(r['personal_number'][4:6])) + ' ' + r['personal_number'][:4] + '.\n'
        else:
            born1 = born[0].split('(')
            assert len(born1) == 2 and born1[1][-1] == ')', (born, born1)
            details = details + u'\nFödd ' + str(int(r['personal_number'][6:8])) + '/' + str(int(r['personal_number'][4:6])) + ' ' + r['personal_number'][:4] + ' i ' + born1[0] + '(' + born1[1][:-1] + ', ' + born[1] + ').\n'
        
        female = int(r['personal_number'][10]) % 2 == 0
        
        civil_change = 'None'
        if r['civil_change'] != '':
            civil_change = str(int(r['civil_change'][6:8])) + '/' + str(int(r['civil_change'][4:6])) + ' ' + r['civil_change'][:4]
        
        civil_state = int(r['civil_state'])
        if civil_state == 1:
            assert r['civil_change'] == ''
            if female:
                civil_state = 'Ogift kvinna'
            else:
                civil_state = 'Ogift man'
        elif civil_state == 2:
            civil_state = 'Gift man (' + civil_change + ')'
        elif civil_state == 3 or civil_state == 7:
           civil_state = 'Gift kvinna (' + civil_change + ')'
        elif civil_state == 4:
            if female:
                civil_state = 'Frånskild kvinna (' + civil_change + ')'
            else:
                civil_state = 'Frånskild man (' + civil_change + ')'
        elif civil_state == 5:
            if female:
                civil_state = 'Änka (' + civil_change + ')'
            else:
                civil_state = 'Änkling (' + civil_change + ')'        
        elif civil_state == 6:
            if female:
                civil_state = 'Avliden kvinna (nov 1990) (' + civil_change + ')'
            else:
                civil_state = 'Avliden man (nov 1990) (' + civil_change + ')'        
        elif civil_state == 8 or civil_state == 9:
            assert r['civil_change'] == ''
            if female:
                civil_state = 'Flicka under 18 år'
            else:
                civil_state = 'Pojke under 18 år'
        else:
            raise Exception(r['civil_state'])
        details = details + '\n' + str(civil_state) + '.\n'
        
        details = details + '--------------\n'
    
        details = details + u'Källor:\nMantalslängd 1991, ' + living[0] + '\n'
        
        return details

    files = {'short_data':                   {'type': 'short_data',    'file_name': 'svbef1990reg.i'},
             'detailed_data':                {'type': 'detailed_data', 'file_name': 'svbef1990reg.b'},
             'last_name':                    {'type': 'index',         'file_name': 'svbef1990reg1.i'},
             'first_name':                   {'type': 'index',         'file_name': 'svbef1990reg2.i'},
             'first_name_number':            {'type': 'index',         'file_name': 'svbef1990reg3.i'},
             'living_county':                {'type': 'index',         'file_name': 'svbef1990reg4.i'}, #län
             'living_municipal':             {'type': 'index',         'file_name': 'svbef1990reg5.i'}, #kommun
             'living_place':                 {'type': 'index',         'file_name': 'svbef1990reg6.i'},
             'living_region':                {'type': 'index',         'file_name': 'svbef1990reg7.i'}, #landskap
             'born':                         {'type': 'index',         'file_name': 'svbef1990reg8.i'},
             'born_county':                  {'type': 'index',         'file_name': 'svbef1990reg9.i'}, # län   
             'unknown':                      {'type': 'index',         'file_name': 'svbef1990re10.i'},
             'birth_date':                   {'type': 'index',         'file_name': 'svbef1990re11.i'},
             'full_address':                 {'type': 'index',         'file_name': 'svbef1990re12.i'},
             'long_estate':                  {'type': 'index',         'file_name': 'svbef1990re13.i'},
             'short_address':                {'type': 'index',         'file_name': 'svbef1990re14.i'},
             'civil_state':                  {'type': 'index',         'file_name': 'svbef1990re15.i'},
             'civil_change':                 {'type': 'index',         'file_name': 'svbef1990re16.i'},
             'personal_number':              {'type': 'index',         'file_name': 'svbef1990re17.i'},
             'short_estate':                 {'type': 'index',         'file_name': 'svbef1990re18.i'}}
    
    short_data_format = [{'name': 'detailed_data_id', 'type': 'uint32'},
                         {'type': 'uint32', 'expected': 0x90},
                         {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\xfe'},
                         {'name': 'birth_date', 'type': 'terminated_string'}]

    detailed_data_format = [{'type': 'uint32', 'expected': 0},
                            {'type': 'uint8', 'expected': 1}, {'name': 'detailed_data_id', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'personal_number', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'name', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'address1', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'address2', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'born', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'living', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'living_estate', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'civil_state', 'type': 'terminated_string'},                             {'type': 'uint8', 'expected': 1}, {'name': 'civil_change', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'estate_number', 'type': 'terminated_string'},
                            {'type': 'atend'}]
            
    local_sub_folders = ['cdbas', 'hdbas']
    local_base_folder = 'SVBEF1990'
    
    def find_same(self, what, data, output):
        if what == 'address':
            post_code = data['address2'].split('  ')
            assert len(post_code) == 2
            search_terms={'full_address': post_code[0] + ';' + data['address1'], 'full_address_match': Match_exact}
            text = 'Samma adress'
        elif what == 'address_and_lastname':
            post_code = data['address2'].split('  ')
            assert len(post_code) == 2
            search_terms={'full_address': post_code[0] + ';' + data['address1'],
                          'full_address_match': Match_exact,
                          'last_name': data['name'].split(', ')[0],
                          'last_name_match': Match_exact}
            text = 'Samma adress och samma efternamn'
        elif what == 'estate':
            search_terms={'long_estate': data['estate_number'] + ';' + data['living_estate'],
                          'long_estate_match': Match_exact}
            text = 'Samma fastighet'
        elif what == 'estate_and_lastname':
            search_terms={'long_estate': data['estate_number'] + ';' + data['living_estate'],
                          'long_estate_match': Match_exact,
                          'last_name': data['name'].split(', ')[0],
                          'last_name_match': Match_exact}
            text = 'Samma fastighet och samma efternamn'
        else:
            raise Exception(what)
    
        return '\n' + text + ':\n' + '\n'.join(self.search_and_parse(search_terms, output=output))

'''
1: Ogift kvinna.
1: Ogift man.
2: Gift man (x).
3: Gift kvinna (x).
4: Frånskild kvinna
4: Frånskild man (x).
5: Änka (x).
5: Änkling (x).
6: Avliden man (nov 1990) (x).
6: Avliden kvinna (nov 1990) (x).
7: Gift kvinna (x).
8: Pojke under 18 år.
8: Flicka under 18 år.
9: Pojke under 18 år.
9: Flicka under 18 år.
'''