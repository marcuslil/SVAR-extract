# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 10:30:22 2014

@author: marcus
"""

from common_search import *

def get_details(r, output='detailed_text'):
    details = u'' + r['personal_number'][:8] + '\n\n' + r['name'] + '\n'
    
    if r['postal_address'] == '' and r['postal_address2'] == '':
        details = details + '\n(Inga adressuppgifter)\n'
    else:
        details = details + '\n' + r['postal_address'] + '\n' + r['postal_address2'] + '\n'

    details = details + u'\nDöd: ' + str(int(r['death_date'][6:])) + '/' + str(int(r['death_date'][4:6])) + ' ' + r['death_date'][:4] + '\n'

    print(list(r['church_register']))
    
    living1 = search_indexed_file(**dict([('search_term', r['church_register']), ('output', ''), ('match', Match_begin)] + setup['files']['scbgam_file'].items()))
    living1 = list(living1)
    assert len(living1) == 1
    living1 = living1[0]
    living1 = living1.split('\r')
    assert living1[0] == r['church_register'], living1[0]
    assert len(living1) == 7, living1
    assert living1[6] == ''
    
    print(living1)
    living_str = living1[5] + '(' + living1[4] + ')\n'
    #print living1

    details = details + '\n' + living_str + '\n' 
    
    living2 = search_indexed_file(**dict([('search_term', living1[1]), ('output', ''), ('match', Match_begin)] + setup['files']['scbny_file'].items()))
    print(living2)

    print(r['born'])
    if r['born'] != '':
        print(r)
        born = search_indexed_file(**dict([('search_term', r['born'] + '\r'), ('output', ''), ('match', Match_begin)] + setup['files']['foort_file'].items()))
        print(born)

    return details
    
#    living = r['living'].split(';')
    assert len(living) == 4
    
    details = details + '\nMantalsskriven i ' +  living[2] + ' (' + living[1] + ', ' + living[0] + ', ' + living[3] + '), fastigheten ' + r['living_estate'] + '.\n'

    born = r['born'].split(';')
    assert len(born) == 2, born
    if born[1] == '[Utomlands]':
        details = details + u'\nFödd ' + str(int(r['personal_number'][6:8])) + '/' + str(int(r['personal_number'][4:6])) + ' ' + r['personal_number'][:4] + '.\n'
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
            civil_state = u'Frånskild kvinna (' + civil_change + ')'
        else:
            civil_state = u'Frånskild man (' + civil_change + ')'
    elif civil_state == 5:
        if female:
            civil_state = u'Änka (' + civil_change + ')'
        else:
            civil_state = u'Änkling (' + civil_change + ')'        
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
        s = search_and_parse(searches={'long_estate': search_term, 'long_estate_match': Match_exact}, output='brief_text')
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
        s = search_and_parse(searches={'full_address': search_term, 'full_address_match': Match_exact, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma adress och samma efternamn:\n' + '\n'.join(s)
    elif output == 'detailed_text_with_same_estate_and_last_name':
        search_term = r['estate_number'] + ';' + r['living_estate']
        last_name = r['name'].split(', ')[0]
        s = search_and_parse(searches={'long_estate': search_term, 'long_estate_match': Match_exact, 'last_name': last_name, 'last_name_match': Match_exact}, output='brief_text')
        details = details + '\nSamma fastighet och samma efternamn:\n' + '\n'.join(s)
    else:
        raise Exception(output)

    return details
    
setup = {'base_folder': '/sharedwine/default/drive_c/Sveriges dödbok 1901-2009', 
         'id1_format': [{'name': 'id2', 'type': 'uint32'},
                        {'type': 'uint32', 'expected': 0x90},
                        {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\r'},
                        {'name': 'birth_date', 'type': 'terminated_string'}],
         'id2_format': [{'type': 'uint32', 'expected': 0},
                        {'type': 'uint8', 'expected': 1}, {'name': 'personal_number', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'sources', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'expected': ''},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'name', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'postal_address', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'postal_address2', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'death_date', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'church_register', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'unknown22', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'unknown24', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'unknown26', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'unknown28', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'gender', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'born', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'name': 'notice1', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'notice2', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 1}, {'name': 'notice3', 'type': 'terminated_string'},
                        {'type': 'uint8', 'expected': 5}, {'type': 'terminated_string', 'excpeted': ''},
                        {'type': 'uint8', 'expected': 5}, {'name': 'notice4', 'type': 'terminated_string'},
                        {'type': 'atend'}],

         'search_fields': ['birth_date','county', 'municpial', 'parish2', 'parish', 'county', 'death_date','last_name', 'first_name','first_name_ordered', 'test'],
         'files': {'id1' : 'sdb5reg.i',
                   'id2' : 'sdb5reg.p',
                   'last_name_index': 'sdb5reg1.i',
                   'first_name_index': 'sdb5reg2.i',
                   'first_name_ordered_index': 'sdb5reg3.i',
                   'death_date_index': 'sdb5reg4.i',
                   'county_index': 'sdb5reg5.i', 
                   'parish_index': 'sdb5reg6.i', 
                   'parish2_index': 'sdb5reg7.i', 
                   'municpial_index': 'sdb5reg8.i', 
                   'county_index': 'sdb5reg9.i', 
                   'birth_date_index': 'sdb5re16.i',
                   'test_index': 'sdb5re18.i',
                   'scbgam_file': 'scbgam.i',
                   'scbny_file': 'scbny.i',
                   'foort_file': 'foort.i' 
                   },
          'get_details': get_details
          }

find_files(setup)

def search_and_parse(**args):
    args['setup'] = setup
    return search_and_parse_setup(**args)
