# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:04:41 2015

@author: marcus
"""

from svardb import SVAR_db
from svarsearch import *

class sveriges_befolkning_1970(SVAR_db):
    def __init__(self):
        pass
        
    def format_short(self, r):
        return r['name'] + '\t' + r['birth_date']        
        #TODO format should yyyy-mm-dd
        
    def format_details(self, r):
        details = u'' + r['birth_date'][:4] + '-' + r['birth_date'][4:6] + '-' + r['birth_date'][6:] + '\n\n' + r['name'] + '\n\n' + r['address'] + '\n' + r['postcode'][:3] + ' ' + r['postcode'][3:] + '  ' + r['postal_address'] + '\n'
        if r['church_reg_parish_nr'] != '':
            krb = self.search_data_reg('living_parish_list', [r['church_reg_parish_nr']])
            assert len(krb) == 5
            details = details + u'\nKyrkobokförd i ' +  krb[3] + ' (' + krb[2] + ', ' + krb[1] + ', ' + krb[4] + '), distrikt ' + r['church_reg_district_nr'] + ', fastighet ' + r['church_reg_estate_nr'] + '. '

        if r['church_reg_parish_nr'] == r['living_reg_pasrish_nr']:
            details = details + u'Mantalsskriven på samma ort.\n'
        else:
            mant = self.search_data_reg('living_parish_list', [r['living_reg_pasrish_nr']])
            assert len(mant) == 5
            details = details + 'Mantalsskriven i ' +  mant[3] + ' (' + mant[2] + ', ' + mant[1] + ', ' + mant[4] + '), distrikt ' + r['living_reg_district_nr'] + ', fastighet ' + r['living_reg_estate_nr'] + '.\n'
        
        born = self.search_data_reg('fo_file', [r['born2'], r['born1']])
        assert len(born) in [5, 6], (born, r)
        if len(born) == 6 and len(born[5]) > 0:
            details = details + u'\nFödd ' + str(int(r['birth_date'][6:])) + '/' + str(int(r['birth_date'][4:6])) + ' ' + r['birth_date'][:4] + ' i ' + born[4] + ' (' + born[3] + ', ' + born[5] + ').\n'
        else: # ignoring "TY"
            details = details + u'\nFödd ' + str(int(r['birth_date'][6:])) + '/' + str(int(r['birth_date'][4:6])) + ' ' + r['birth_date'][:4] + '.\n'
        source = int(r['source']) - 1
        assert source != 1, source
        if source > 1:
            source -= 1        
        details = details + u'--------------\nKälla: ' + self.sources[source] + '\n'

        return details
                
    files = {'short_data':                      {'type': 'short_data',    'file_name': 'ma70reg.i'},
             'detailed_data':                   {'type': 'detailed_data', 'file_name': 'ma70reg.b'}, 
             'last_name':                       {'type': 'index',         'file_name': 'ma70reg1.i'},
             'first_name':                      {'type': 'index',         'file_name': 'ma70reg2.i'},
             'first_name_ordered':              {'type': 'index',         'file_name': 'ma70reg3.i'},
             'living_and church_reg_county':    {'type': 'index',         'file_name': 'ma70reg4.i'}, #county=län
             'living_and_church_reg_municipal': {'type': 'index',         'file_name': 'ma70reg5.i'}, #municipal=kommun
             'living_and_church_reg_parish' :   {'type': 'index',         'file_name': 'ma70reg6.i'}, #parish=församling
             'living_and_church_reg_region' :   {'type': 'index',         'file_name': 'ma70reg7.i'}, #region=landskap
             'born_parish':                     {'type': 'index',         'file_name': 'ma70reg8.i'},
             'born_county':                     {'type': 'index',         'file_name': 'ma70reg9.i'},
             'born_region':                     {'type': 'index',         'file_name': 'ma70re10.i'},
             'birth_date':                      {'type': 'index',         'file_name': 'ma70re11.i'},
             'full_address' :                   {'type': 'index',         'file_name': 'ma70re12.i', 'local_file_ignore_accents': True},
             'church_reg_parish_estate':        {'type': 'index',         'file_name': 'ma70re13.i'},
             'short_address' :                  {'type': 'index',         'file_name': 'ma70re14.i'},
             'fo_file':                         {'type': 'data',          'file_name': 'ma70fo.i', 'local_file_ignore_accents': True},
             'living_parish_list':              {'type': 'data',          'file_name': 'ma70bo.i'}}
    
    short_data_format = [{'name': 'detailed_data_id', 'type': 'uint32'},
                         {'type': 'uint32', 'expected': 0x90},
                         {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\r'},
                         {'name': 'birth_date', 'type': 'terminated_string'},
                         {'type': 'zeros', 'length': -1}]
        
    detailed_data_format = [{'type': 'uint32', 'expected': 0},
                            {'type': 'uint8', 'expected': 1}, {'name': 'birth_date', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'source', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'name', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'address', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'postcode', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'postal_address', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'born1', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'born2', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'church_reg_parish_nr', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'church_reg_district_nr', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'church_reg_estate_nr', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'living_reg_pasrish_nr', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'living_reg_district_nr', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'living_reg_estate_nr', 'type': 'terminated_string'},
                            {'type': 'atend'}]

    sources = [u'Mtl Stockholms stad och l\xe4n 1971', u'Mtl Uppsala l\xe4n 1971', u'Mtl S\xf6dermanlands l\xe4n 1971', u'Mtl \xd6sterg\xf6tlands l\xe4n 1971', u'Mtl J\xf6nk\xf6pings l\xe4n 1971', u'Mtl Kronobergs l\xe4n 1971', u'Mtl Kalmar l\xe4n 1971', u'Mtl Gotlands l\xe4n 1971', u'Mtl Blekinge l\xe4n 1971', u'Mtl Kristianstads l\xe4n 1971', u'Mtl Malm\xf6hus l\xe4n 1971', u'Mtl Hallands l\xe4n 1971', u'Mtl G\xf6teborgs och Bohus l\xe4n 1971', u'Mtl \xc4lvsborgs l\xe4n 1971', u'Mtl Skaraborgs l\xe4n 1971', u'Mtl V\xe4rmlands l\xe4n 1971', u'Mtl \xd6rebro l\xe4n 1971', u'Mtl V\xe4stmanlands l\xe4n 1972', u'Mtl Kopparbergs l\xe4n 1971', u'Mtl G\xe4vleborgs l\xe4n 1971', u'Mtl V\xe4sternorrlands l\xe4n 1971', u'Mtl J\xe4mtlands l\xe4n 1971', u'Mtl V\xe4sterbottens l\xe4n 1971', u'Mtl Norrbottens l\xe4n 1971']

    local_sub_folders = ['cdbas', 'hdbas']
    local_base_folder = 'SVBEF70'

    def find_same(self, what, data, output):
        if what == 'address':
            search_terms={'full_address': data['postcode'] + ';' + data['postal_address'] + ';' + data['address'],
                          'full_address_match': Match_exact}
            text = 'Samma adress'
        elif what == 'address_and_lastname':
            search_terms={'full_address': data['postcode'] + ';' + data['postal_address'] + ';' + data['address'],
                          'full_address_match': Match_exact,
                          'last_name': data['name'].split(', ')[0],
                          'last_name_match': Match_exact}
            text = 'Samma adress och samma efternamn'
        elif what == 'estate':
            search_terms={'church_reg_parish_estate': data['church_reg_parish_nr'] + ';' + data['church_reg_district_nr'] + ';' + data['church_reg_estate_nr'],
                          'church_reg_parish_estate_match': Match_exact}
            text = 'Samma fastighet'
        elif what == 'estate_and_lastname':
            search_terms={'church_reg_parish_estate': data['church_reg_parish_nr'] + ';' + data['church_reg_district_nr'] + ';' + data['church_reg_estate_nr'],
                          'church_reg_parish_estate_match': Match_exact,
                          'last_name': data['name'].split(', ')[0],
                          'last_name_match': Match_exact}
            text = 'Samma fastighet och samma efternamn'
        else:
            raise Exception(what)

        return '\n' + text + ':\n' + '\n'.join(self.search_and_parse(search_terms, output=output))
