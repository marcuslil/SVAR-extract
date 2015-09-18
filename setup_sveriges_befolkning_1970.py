# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:04:41 2015

@author: marcus
"""

from common_search import *

def get_short(r):
    return r['name'] + '\t' + r['birth_date']
    #[:4] + '-' + r['birth_date'][4:6] + '-' + r['birth_date'][6:8]

def get_details(r, output='detailed_text'):
    details = u'' + r['birth_date'][:4] + '-' + r['birth_date'][4:6] + '-' + r['birth_date'][6:] + '\n\n' + r['name'] + '\n\n' + r['address'] + '\n' + r['postcode'][:3] + ' ' + r['postcode'][3:] + '  ' + r['postal_address'] + '\n'
    krb = search_indexed_file(**dict([('search_term', r['church_reg_parish_nr'] + ';'), ('output', ''), ('match', Match_begin)] + list(setup['files']['living_parish_list'].items())))
    assert len(krb) == 1, krb
    krb = list(krb)[0].split(';')
    assert len(krb) == 5 and krb[0] == r['church_reg_parish_nr']
    details = details + u'\nKyrkobokförd i ' +  krb[3] + ' (' + krb[2] + ', ' + krb[1] + ', ' + krb[4] + '), distrikt ' + r['church_reg_district_nr'] + ', fastighet ' + r['church_reg_estate_nr'] + '.'
    if r['church_reg_parish_nr'] == r['living_reg_pasrish_nr']:
        details = details + u' Mantalsskriven på samma ort.\n'
    else:
        mant = search_indexed_file(**dict([('search_term', r['living_reg_pasrish_nr'] + ';'), ('output', ''), ('match', Match_begin)] + setup['files']['living_parish_list'].items()))
        assert len(mant) == 1, mant
        mant = list(mant)[0].split(';')
        assert len(mant) == 5 and mant[0] == r['living_reg_pasrish_nr']
        details = details + ' Mantalsskriven i ' +  mant[3] + ' (' + mant[2] + ', ' + mant[1] + ', ' + mant[4] + '), distrikt ' + r['living_reg_district_nr'] + ', fastighet ' + r['living_reg_estate_nr'] + '.\n'
    
    search_term = r['born2'] + ';' + r['born1'] + ';'
    born = search_indexed_file(**dict([('search_term', search_term), ('output', ''), ('match', Match_begin)] + list(setup['files']['fo_file'].items())))
    assert len(born) == 1, born
    born = list(born)[0].split(';')
    assert len(born) in [5, 6] and born[0] == r['born2'] and born[1] == r['born1'], (born, r)
    if len(born) == 6 and len(born[5]) > 0:
        details = details + u'\nFödd ' + str(int(r['birth_date'][6:])) + '/' + str(int(r['birth_date'][4:6])) + ' ' + r['birth_date'][:4] + ' i ' + born[4] + ' (' + born[3] + ', ' + born[5] + ').\n'
    else: # ignoring "TY"
        details = details + u'\nFödd ' + str(int(r['birth_date'][6:])) + '/' + str(int(r['birth_date'][4:6])) + ' ' + r['birth_date'][:4] + '.\n'
    source = int(r['source']) - 1
    assert source != 1, source
    if source > 1:
        source -= 1        
    details = details + u'--------------\nKälla: ' + setup['sources'][source] + '\n'
    
    if output == 'detailed_text':
        pass
    elif output == 'detailed_text_with_same_address':
        search_term = r['postcode'] + ';' + r['postal_address'] + ';' + r['address']
        s = search_and_parse(searches={'full_address': search_term, 'full_address_match': Match_exact_ignore_accents}, output='brief_text')
        details = details + '\nSamma adress:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_address_and_last_name':
        search_term = r['postcode'] + ';' + r['postal_address'] + ';' + r['address']
        last_name = r['name'].split(', ')[0]
        s = search_and_parsep(searches={'full_address': search_term, 'full_address_match': Match_exact_ignore_accents, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma adress och samma efternamn:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_estate':
        search_term = r['church_reg_parish_nr'] + ';' + r['church_reg_district_nr'] + ';' + r['church_reg_estate_nr']
        s = search_and_parse(searches={'church_reg_parish_estate': search_term, 'church_reg_parish_estate_match': Match_exact}, output='brief_text')
        details = details + '\nSamma fastighet adress:\n' + '\n'.join(s)        
    elif output == 'detailed_text_with_same_estate_and_last_name':
        search_term = r['church_reg_parish_nr'] + ';' + r['church_reg_district_nr'] + ';' + r['church_reg_estate_nr']
        last_name = r['name'].split(', ')[0]
        s = search_and_parse(searches={'church_reg_parish_estate': search_term, 'church_reg_parish_estate_match': Match_exact, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma fastighet adress:\n' + '\n'.join(s)        
    else:
        raise Exception(output)

    return details

setup = {'base_folder': '/sharedwine/default/drive_c/SVBEF70',
         'id1_format': [{'name': 'id2', 'type': 'uint32'},
                        {'type': 'uint32', 'expected': 0x90},
                        {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\r'},
                        {'name': 'birth_date', 'type': 'terminated_string'},
                        {'type': 'zeros', 'length': -1}],
        
         'id2_format': [{'type': 'uint32', 'expected': 0},
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
                        {'type': 'atend'}],

         'sources': [u'Mtl Stockholms stad och l\xe4n 1971', u'Mtl Uppsala l\xe4n 1971', u'Mtl S\xf6dermanlands l\xe4n 1971', u'Mtl \xd6sterg\xf6tlands l\xe4n 1971', u'Mtl J\xf6nk\xf6pings l\xe4n 1971', u'Mtl Kronobergs l\xe4n 1971', u'Mtl Kalmar l\xe4n 1971', u'Mtl Gotlands l\xe4n 1971', u'Mtl Blekinge l\xe4n 1971', u'Mtl Kristianstads l\xe4n 1971', u'Mtl Malm\xf6hus l\xe4n 1971', u'Mtl Hallands l\xe4n 1971', u'Mtl G\xf6teborgs och Bohus l\xe4n 1971', u'Mtl \xc4lvsborgs l\xe4n 1971', u'Mtl Skaraborgs l\xe4n 1971', u'Mtl V\xe4rmlands l\xe4n 1971', u'Mtl \xd6rebro l\xe4n 1971', u'Mtl V\xe4stmanlands l\xe4n 1972', u'Mtl Kopparbergs l\xe4n 1971', u'Mtl G\xe4vleborgs l\xe4n 1971', u'Mtl V\xe4sternorrlands l\xe4n 1971', u'Mtl J\xe4mtlands l\xe4n 1971', u'Mtl V\xe4sterbottens l\xe4n 1971', u'Mtl Norrbottens l\xe4n 1971'],

         'search_fields': ['last_name',
                           'first_name',
                           'first_name_ordered',
                           'living_and church_reg_county',
                           'living_and_church_reg_municipal',
                           'living_and_church_reg_parish',
                           'living_and_church_reg_region',
                           'born_parish',
                           'born_county',
                           'born_region',
                           'birth_date',
                           'full_address',
                           'church_reg_parish_estate',
                           'short_address'],

         'files': {'id1' :                                  'ma70reg.i',
                   'id2' :                                  'ma70reg.p',
                   'last_name_index':                       'ma70reg1.i',
                   'first_name_index':                      'ma70reg2.i',
                   'first_name_ordered_index':              'ma70reg3.i',
                   'living_and church_reg_county_index':    'ma70reg4.i', #county=län
                   'living_and_church_reg_municipal_index': 'ma70reg5.i', #municipal=kommun
                   'living_and_church_reg_parish_index' :   'ma70reg6.i', #parish=församling
                   'living_and_church_reg_region_index' :   'ma70reg7.i', #region=landskap
                   'born_parishsetup_sveriges_befolkning_1990_index':                     'ma70reg8.i',
                   'born_cousetup_sveriges_befolkning_1990nty_index':                     'ma70reg9.i',
                   'born_region_index':                     'ma70re10.i',
                   'birth_date_index':                      'ma70re11.i',
                   'full_address_index' :                   'ma70re12.i',
                   'church_reg_parish_estate_index':        'ma70re13.i',
                   'short_address_index' :                  'ma70re14.i',
                   'fo_file':                               'ma70fo.i',
                   'living_parish_list':                    'ma70bo.i'},

         'get_details': get_details,
         'get_short': get_short
         }

find_files(setup)
setup['files']['full_address_index']['file_ignore_accents'] = True
setup['files']['fo_file']['file_ignore_accents'] = True

def search_and_parse(**args):
    args['setup'] = setup
    return search_and_parse_setup(**args)
