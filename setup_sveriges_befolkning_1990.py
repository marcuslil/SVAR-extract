# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 19:30:57 2015

@author: marcus
"""

from common_search import *

def get_short(r):
    return r['name'] + '\t' + r['birth_date'][:4] + '-' + r['birth_date'][4:6] + '-' + r['birth_date'][6:8]

def get_details(r, output='detailed_text'):
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
    
    if output ==  'detailed_text':
        pass       
    elif output == 'detailed_text_with_same_estate':
        search_term = r['estate_number'] + ';' + r['living_estate']
        s = search_and_parse( searches={'long_estate': search_term, 'long_estate_match': Match_exact}, output='brief_text')
        details = details + '\nSamma fastighet:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_address':
        post_code = r['address2'].split('  ')
        assert len(post_code) == 2
        search_term =post_code[0] + ';' + r['address1']
        s = search_and_parse(searches={'full_address': search_term, 'full_address_match': Match_exact}, output='brief_text')
        details = details + '\nSamma adress:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_address_and_last_name':
        post_code = r['address2'].split('  ')
        assert len(post_code) == 2
        search_term =post_code[0] + ';' + r['address1']
        last_name = r['name'].split(', ')[0]
        s = search_and_parse( searches={'full_address': search_term, 'full_address_match': Match_exact, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma adress och samma efternamn:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_estate_and_last_name':
        search_term = r['estate_number'] + ';' + r['living_estate']
        last_name = r['name'].split(', ')[0]
        s = search_and_parse(searches={'long_estate': search_term, 'long_estate_match': Match_exact, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma fastighet och samma efternamn:\n' + '\n'.join(s)
    else:
        raise Exception(output)

    return details
    
setup = {'base_folder': '/sharedwine/default/drive_c/SVBEF1990',
         'id1_format': [{'name': 'id2', 'type': 'uint32'},
                        {'type': 'uint32', 'expected': 0x90},
                        {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\xfe'},
                        {'name': 'birth_date', 'type': 'terminated_string'}],
         'id2_format': [{'type': 'uint32', 'expected': 0},
                        {'type': 'uint8', 'expected': 1}, {'name': 'id2', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'personal_number', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'name', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'address1', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'address2', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'born', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'living', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'living_estate', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'civil_state', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'civil_change', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'estate_number', 'type': 'terminated_string'},
                        {'type': 'atend'}],

         'search_fields': ['test1', 'last_name', 'first_name', 'full_address', 'short_address', 'long_estate', 'born', 'born_county', 'living_municipal', 'living_place', 'living_county', 'living_region', 'short_estate', 'short_address', 'civil_state', 'living_country', 'birth_date', 'civil_change', 'personal_number',  'full_address'],
         'files': {'id1' :                   'svbef1990reg.i',
                   'id2' :                   'svbef1990reg.p',
                   'full_address_index':     'svbef1990re12.i', 
                   'short_address_index':    'svbef1990re14.i', 
                   'last_name_index':        'svbef1990reg1.i',
                   'birth_date_index':       'svbef1990re11.i',
                   'personal_number_index':  'svbef1990re17.i',
                   'long_estate_index':      'svbef1990re13.i',
                   'civil_state_index':      'svbef1990re15.i', 
                   'civil_change_index':     'svbef1990re16.i',
                   'short_estate_index':     'svbef1990re18.i',
                   'first_name_index':       'svbef1990reg2.i',
                   'first_name_number_index':'svbef1990reg3.i',
                   'living_municipal_index': 'svbef1990reg5.i', # kommun
                   'living_place_index':     'svbef1990reg6.i',
                   'living_county_index':    'svbef1990reg4.i', # län
                   'living_region_index':    'svbef1990reg7.i', # landskap
                   'born_index':             'svbef1990reg8.i',
                   'born_county_index':      'svbef1990reg9.i'}, # län
                   #left svbef1990re10.i
         'get_details': get_details,
         'get_short': get_short
         }
              

find_files(setup)

def search_and_parse(**args):
    args['setup'] = setup
    return search_and_parse_setup(**args)