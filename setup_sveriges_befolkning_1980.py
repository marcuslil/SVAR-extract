# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:26:46 2015

@author: marcus
"""

from svardb import SVAR_db
from svarsearch import *

class sveriges_befolkning_1980(SVAR_db):
    def __init__(self):
        pass
        
    def format_short(self, r):
        return r['name'] + '\t' + r['birth_date']    
                
    def format_details(self, r):
        details = u'' + r['birth_date'][:4] + '-' + r['birth_date'][4:6] + '-' + r['birth_date'][6:] + '\n\n' + r['name'] + '\n'
        
        if r['address'] == '' and r['postcode'] == '' and r['postal_address'] == '':
            details = details + '\n(Inga adressuppgifter)\n'
        else:
            details = details + '\n' + r['address'] + '\n' + r['postcode'][:3] + ' ' + r['postcode'][3:] + '  ' + r['postal_address'] + '\n'

        living = self.search_data_reg('living_parish_list', [r['living_reg_pasrish_nr']])
        assert len(living) == 5, living
        details = details + '\nMantalsskriven i ' +  living[3] + ' (' + living[2] + ', ' + living[1] + ', ' + living[4] + '), fastigheten ' + r['living_reg_estate_nr'] + '.\n'

        born = self.search_data_reg('fo_file', [r['born2'], r['born1']])
        assert len(born) in [5, 6], (born, r)
        if born[4].endswith(' '):
            born[4] = born[4][:-1]
        if len(born) == 6 and len(born[3]) > 0:
            details = details + u'\nFödd ' + str(int(r['birth_date'][6:])) + '/' + str(int(r['birth_date'][4:6])) + ' ' + r['birth_date'][:4] + ' i ' + born[4] + ' (' + born[3] + ', ' + born[5] + ').\n'
        else: # ignoring "TY"
            details = details + u'\nFödd ' + str(int(r['birth_date'][6:])) + '/' + str(int(r['birth_date'][4:6])) + ' ' + r['birth_date'][:4] + '.\n'
    
        source = int(r['source']) - 1
        assert source != 1, source
        if r['source'] == '14':
            raise Exception('source = 14')
        if source > 1:
            source -= 1
        if source > 12:
            source += 1
        if r['source'] == '79':
            source = 12
        elif r['source'] == '81':
            source = 13
        elif r['source'] == '99':
            source = 25
        details = details + u'--------------\nKälla: ' + self.sources[source] + '\n'
        
        return details

    def find_same(self, what, data, output):
        if what == 'address':
            search_terms={'full_address': data['postcode'] + ';' + data['postal_address'] + ';' + data['address']}
            text = 'Samma adress'
        elif what == 'address_and_lastname':
            search_terms={'full_address': data['postcode'] + ';' + data['postal_address'] + ';' + data['address'],
                          'full_address_match': Match_exact,
                          'last_name': data['name'].split(', ')[0],
                          'last_name_match': Match_exact}
            text = 'Samma adress och samma efternamn'
        elif what == 'estate':
            search_terms={'living_reg_parish_estate': data['living_reg_pasrish_nr'] + ';' + data['living_reg_estate_nr'],
                          'living_reg_parish_estate_match': Match_exact}
            text = 'Samma fastighet'
        elif what == 'estate_and_lastname':
            search_terms={'living_reg_parish_estate': data['living_reg_pasrish_nr'] + ';' + data['living_reg_estate_nr'],
                          'living_reg_parish_estate_match': Match_exact,
                          'last_name': data['name'].split(', ')[0],
                          'last_name_match': Match_exact}
            text = 'Samma fastighet och samma efternamn'
        else:
            raise Exception(what)

        return '\n' + text + ':\n' + '\n'.join(self.search_and_parse(search_terms, output=output))
       
    local_sub_folders = ['cdbas', 'hdbas']
    local_base_folder = 'SVBEF80'


    sources = [u'Mtl Stockholm l\xe4n 1981', u'Mtl Uppsala l\xe4n 1981', u'Mtl S\xf6dermanlands l\xe4n 1981', u'Mtl \xd6sterg\xf6tlands l\xe4n 1981', u'Mtl J\xf6nk\xf6pings l\xe4n 1981', u'Mtl Kronobergs l\xe4n 1981', u'Mtl Kalmar l\xe4n 1981', u'Mtl Gotlands l\xe4n 1981', u'Mtl Blekinge l\xe4n 1981', u'Mtl Kristianstads l\xe4n 1981', u'Mtl Malm\xf6hus l\xe4n 1981', u'Mtl Hallands l\xe4n 1981', u'Mtl G\xf6teborgs och Bohus l\xe4n 1980', u'Mtl G\xf6teborgs och Bohus l\xe4n 1982', u'Mtl \xc4lvsborgs l\xe4n 1981', u'Mtl Skaraborgs l\xe4n 1981', u'Mtl V\xe4rmlands l\xe4n 1981', u'Mtl \xd6rebro l\xe4n 1981', u'Mtl V\xe4stmanlands l\xe4n 1981', u'Mtl Kopparbergs l\xe4n 1981', u'Mtl G\xe4vleborgs l\xe4n 1981', u'Mtl V\xe4sternorrlands l\xe4n 1981', u'Mtl J\xe4mtlands l\xe4n 1981', u'Mtl V\xe4sterbottens l\xe4n 1981', u'Mtl Norrbottens l\xe4n 1981', u'Mtl Sverige 1981']


    short_data_format = [{'name': 'detailed_data_id', 'type': 'uint32'},
                         {'type': 'uint32', 'expected': 0x90},
                         {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\r'},
                         {'name': 'birth_date', 'type': 'terminated_string'}]
        
    detailed_data_format =  [{'type': 'uint32', 'expected': 0},
                             {'type': 'uint8', 'expected': 1}, {'name': 'birth_date', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'source', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'name', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'address', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'postcode', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'postal_address', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'born1', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'born2', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'living_reg_pasrish_nr', 'type': 'terminated_string'},
                             {'type': 'uint8', 'expected': 1}, {'name': 'living_reg_estate_nr', 'type': 'terminated_string'},
                             {'type': 'atend'}]

    files = {'short_data' :             {'type': 'short_data',    'file_name': 'ma80reg.i'},
             'detailed_data' :          {'type': 'detailed_data', 'file_name': 'ma80reg.b'}, 
             'last_name':               {'type': 'index',         'file_name': 'ma80reg1.i'},
             'first_name':              {'type': 'index',         'file_name': 'ma80reg2.i'},
             'first_name_ordered':      {'type': 'index',         'file_name': 'ma80reg3.i'},
             'living_reg_county':       {'type': 'index',         'file_name': 'ma80reg4.i'}, #county=län
             'living_reg_municipal':    {'type': 'index',         'file_name': 'ma80reg5.i'}, #municipal=kommun
             'living_reg_parish' :      {'type': 'index',         'file_name': 'ma80reg6.i'}, #parish=församling
             'living_reg_region' :      {'type': 'index',         'file_name': 'ma80reg7.i'}, #region=landskap
             'born_parish':             {'type': 'index',         'file_name': 'ma80reg8.i'},
             'born_county':             {'type': 'index',         'file_name': 'ma80reg9.i'},
             'born_region':             {'type': 'index',         'file_name': 'ma80re10.i'},
             'birth_date':              {'type': 'index',         'file_name': 'ma80re11.i'},
             'full_address' :           {'type': 'index',         'file_name': 'ma80re12.i'},
             'living_reg_parish_estate':{'type': 'index',         'file_name': 'ma80re13.i'},
             'short_address' :          {'type': 'index',         'file_name': 'ma80re14.i'},
             'fo_file':                 {'type': 'data',          'file_name': 'ma80fo.i', 'local_file_ignore_accents': True},
             'living_parish_list':      {'type': 'data',          'file_name': 'ma80bo.i'}}
             