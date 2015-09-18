# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:26:46 2015

@author: marcus
"""

from common_search import *

from setup_sveriges_befolkning_1970 import get_short
                
def get_details(r, output='detailed_text'):
    details = u'' + r['birth_date'][:4] + '-' + r['birth_date'][4:6] + '-' + r['birth_date'][6:] + '\n\n' + r['name'] + '\n'
    
    if r['address'] == '' and r['postcode'] == '' and r['postal_address'] == '':
        details = details + '\n(Inga adressuppgifter)\n'
    else:
        details = details + '\n' + r['address'] + '\n' + r['postcode'][:3] + ' ' + r['postcode'][3:] + '  ' + r['postal_address'] + '\n'
    living = search_indexed_file(**dict({'search_term': r['living_reg_pasrish_nr'] + ';', 'output': '', 'match': Match_begin}.items() | setup['files']['living_parish_list'].items()))
    assert len(living) in [0,1], living
    if len(living) == 1:
        living = list(living)[0].split(';')
        assert len(living) == 5 and living[0] == r['living_reg_pasrish_nr']
        details = details + '\nMantalsskriven i ' +  living[3] + ' (' + living[2] + ', ' + living[1] + ', ' + living[4] + '), fastigheten ' + r['living_reg_estate_nr'] + '.\n'
    
    search_term = r['born2'] + ';' + r['born1'] + ';'
    born = search_indexed_file(**dict([('search_term', search_term), ('output', ''), ('match', Match_begin)] + list(setup['files']['fo_file'].items())))
    assert len(born) == 1, born
    born = list(born)[0].split(';')
    assert len(born) in [5, 6] and born[0] == r['born2'] and born[1] == r['born1'], (born, r)
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
    details = details + u'--------------\nKälla: ' + setup['sources'][source] + '\n'
    
    
    if output == 'detailed_text':
        pass
    elif output == 'detailed_text_with_same_address':
        search_term = r['postcode'] + ';' + r['postal_address'] + ';' + r['address']
        s = search_and_parse(searches={'full_address': search_term, 'full_address_match': Match_exact}, output='brief_text')
        details = details + '\nSamma adress:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_address_and_last_name':
        search_term = r['postcode'] + ';' + r['postal_address'] + ';' + r['address']
        last_name = r['name'].split(', ')[0]
        s = search_and_parse(searches={'full_address': search_term, 'full_address_match': Match_exact, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma adress och samma efternamn:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_estate':
        search_term = r['living_reg_pasrish_nr'] + ';' + r['living_reg_estate_nr'] 
        s = search_and_parse(searches={'living_reg_parish_estate': search_term, 'living_reg_parish_estate_match': Match_exact}, output='brief_text')
        details = details + '\nSamma fastighet:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_estate_and_last_name':
        search_term = r['living_reg_pasrish_nr'] + ';' + r['living_reg_estate_nr'] 
        last_name = r['name'].split(', ')[0]
        s = search_and_parse(searches={'living_reg_parish_estate': search_term, 'living_reg_parish_estate_match': Match_exact, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma fastighet och samma efternamn:\n' + '\n'.join(s)
    else:
        raise Exception(output)

    return details

setup = {'base_folder': '/sharedwine/default/drive_c/SVBEF80',
         'id1_format': [{'name': 'id2', 'type': 'uint32'},
                        {'type': 'uint32', 'expected': 0x90},
                        {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\r'},
                        {'name': 'birth_date', 'type': 'terminated_string'}],
         'id2_format': [{'type': 'uint32', 'expected': 0},
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
                        {'type': 'atend'}], 

         'sources': [u'Mtl Stockholm l\xe4n 1981', u'Mtl Uppsala l\xe4n 1981', u'Mtl S\xf6dermanlands l\xe4n 1981', u'Mtl \xd6sterg\xf6tlands l\xe4n 1981', u'Mtl J\xf6nk\xf6pings l\xe4n 1981', u'Mtl Kronobergs l\xe4n 1981', u'Mtl Kalmar l\xe4n 1981', u'Mtl Gotlands l\xe4n 1981', u'Mtl Blekinge l\xe4n 1981', u'Mtl Kristianstads l\xe4n 1981', u'Mtl Malm\xf6hus l\xe4n 1981', u'Mtl Hallands l\xe4n 1981', u'Mtl G\xf6teborgs och Bohus l\xe4n 1980', u'Mtl G\xf6teborgs och Bohus l\xe4n 1982', u'Mtl \xc4lvsborgs l\xe4n 1981', u'Mtl Skaraborgs l\xe4n 1981', u'Mtl V\xe4rmlands l\xe4n 1981', u'Mtl \xd6rebro l\xe4n 1981', u'Mtl V\xe4stmanlands l\xe4n 1981', u'Mtl Kopparbergs l\xe4n 1981', u'Mtl G\xe4vleborgs l\xe4n 1981', u'Mtl V\xe4sternorrlands l\xe4n 1981', u'Mtl J\xe4mtlands l\xe4n 1981', u'Mtl V\xe4sterbottens l\xe4n 1981', u'Mtl Norrbottens l\xe4n 1981', u'Mtl Sverige 1981'],


        'search_fields': ['last_name',
                           'first_name',
                           'first_name_ordered',
                           'living_reg_county',
                           'living_reg_municipal',
                           'living_reg_parish',
                           'living_reg_region',
                           'born_parish',
                           'born_county',
                           'born_region',
                           'birth_date',
                           'full_address',
                           'living_reg_parish_estate',
                           'short_address'],

         'files': {'id1' :                       'ma80reg.i',
                   'id2' :                       'ma80reg.p',
                   'last_name_index':            'ma80reg1.i',
                   'first_name_index':           'ma80reg2.i',
                   'first_name_ordered_index':   'ma80reg3.i',
                   'living_reg_county_index':    'ma80reg4.i', #county=län
                   'living_reg_municipal_index': 'ma80reg5.i', #municipal=kommun
                   'living_reg_parish_index' :   'ma80reg6.i', #parish=församling
                   'living_reg_region_index' :   'ma80reg7.i', #region=landskap
                   'born_parish_index':          'ma80reg8.i',
                   'born_county_index':          'ma80reg9.i',
                   'born_region_index':          'ma80re10.i',
                   'birth_date_index':           'ma80re11.i',
                   'full_address_index' :        'ma80re12.i',
                   'living_reg_parish_estate_index':'ma80re13.i',
                   'short_address_index' :       'ma80re14.i',
                   'fo_file':                    'ma80fo.i',
                   'living_parish_list':         'ma80bo.i'},

         'get_details': get_details,
         'get_short': get_short
         }

find_files(setup)
setup['files']['fo_file']['file_ignore_accents'] = True

def search_and_parse(**args):
    args['setup'] = setup
    return search_and_parse_setup(**args)