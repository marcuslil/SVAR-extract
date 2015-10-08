# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 10:30:22 2014

@author: marcus
"""

from svardb import SVAR_db
from svarsearch import *

class sveriges_dodbok_2009(SVAR_db):
    def __init__(self):
        pass
    
    def search_scbgam_file(self, id_name, year1, year2):
        ret_new= []
        if year1 != '':
            year = int(year1) + 1900
            ret_year = '(' + str(year) + ') '
        else:
            year = int(year2[:4])
            ret_year = ''

        result = self.local_files['scbgam_file'].search(id_name, Match_begin, return_type=SVAR_search_return.data)
        if len(result) == 0:
            return ret_year, 'Församling med SCB-kod ' + id_name, ret_new
        found = None
        for line in result:
            line = line.split('\r')
            if int(line[1]) <= year and int(line[2]) >= year:
                if not found:
                    found = line
                if not line[0] in ret_new:
                    ret_new.append(line[0])
        assert found, (result, year, found, id_name)
        assert len(found) == 6, found
        return ret_year, self.format_parish(found[3:]), ret_new        
        
    def format_parish(self, parish):
        assert len(parish) == 3, parish
        if parish[2] != '':
            assert parish[0:2] == [';;', '']
            formatted = parish[2]
        else:
            a = parish[0].split(';')
            assert len(a) == 3, a
            if a[1] != '':
                a[1] = ', ' + a[1]
            formatted = a[2] + a[1] + ' (' + a[0]
            if parish[1] != '':
                formatted += ', ' + parish[1]
            formatted += ')'
        return formatted
        
        
    def calc_years_old(self, born, death):
        years_old = int(death[:4]) - int(born[:4])
        if len(death) > 4 and death[4:6] != '00' and len(born) > 4 and born[4:6] != '00':
            if int(born[4:6]) > int(death[4:6]):
                years_old -= 1
            if born[4:6] == death[4:6] and len(death) > 6 and death[6:8] != '00' and len(born) > 6 and born[6:8] != '00':
                if int(born[6:8]) > int(death[6:8]):
                    years_old -= 1
        return years_old
                
        
    def format_date(self, date):
        day = str(int(date[6:8])) if len(date) > 6 and date[6:8] != '00' else '?'
        month = str(int(date[4:6])) if len(date) > 4 and date[4:6] != '00' else '?'
        if day == '?' and month == '?':
            return date[:4]
        else:
            return day + '/' + month + ' ' + date[:4]
    
    def format_details(self, r):
        details = u'' + r['personal_number'][:8]
        if len(r['personal_number']) > 8:
            details += '-' + r['personal_number'][8:]
        details +='\n\n'
        name = r['name']
        if name.startswith(','):
            name = name[1:]
        if name == '' and r['postal_address'] == '' and r['postal_address2'] == '':
            details += '(Inga namn- eller adressuppgifter)\n\n'
        else:
            if name == '':
                details += '(Ingen namnuppgift)\n\n'            
            else:
                details += name + '\n\n'
        
            if r['postal_address'] == '' and r['postal_address2'] == '':
                details += '(Inga adressuppgifter)\n\n'
            else:
                if r['postal_address'] != '':
                    details += r['postal_address'] + '\n'
                if r['postal_address2'] != '':
                    details += r['postal_address2'] + '\n'
                details += '\n'
       
        details += u'Död ' + self.format_date(r['death_date'])+ '.\n\n'
 
        churchreg = [r['churchreg_id'], r['churchreg_year'], r['churchreg_?']]
        livingreg = [r['livingreg_id'], r['livingreg_year'], r['livingreg_?']]
        if r['churchreg_id'] != '':
            year, place, new_parish = self.search_scbgam_file(r['churchreg_id'], r['churchreg_year'], r['death_date'])
            details += u'Kyrkobokförd ' + year + 'i ' + place +'.'
            
        if r['livingreg_id'] != '':
            if details[-1] == '.':
                details += ' '
            if churchreg == livingreg:
                if r['livingreg_year'] != '':
                    year = '(19' + r['livingreg_year'] + ') '
                else:   
                    year = ''
                details += u'Mantalsskriven ' + year + 'på samma ort.'
            else:
                year, place, _ = self.search_scbgam_file(r['livingreg_id'], r['livingreg_year'], r['death_date'])
                details += u'Mantalskriven ' + year + 'i ' + place +'.'
        
        if r['residence_id'] != '' and r['churchreg_id'] == '' and r['livingreg_id'] == '':
            year, place, _ = self.search_scbgam_file(r['residence_id'], r['residence_year'], r['death_date'])
            details += u'Folkbokförd ' + year + 'i ' + place +'.'

        if details[-1] == '.':
            details += '\n\n'

        details += u'Född ' + self.format_date(r['personal_number']) + ' '

        if r['born_place1'] != '':
            born_place = self.local_files['foort_file'].search(r['born_place1'] + r['born_place2'], return_type=SVAR_search_return.data)[0].split('\r')
            assert len(born_place) == 3, born_place
            if born_place[2] == '':
                assert born_place[0][-1] == ')'
                born_place[0] = born_place[0][:-1].split('(')
                assert len(born_place[0]) == 2
                born_place_text = born_place[0][0] + '(' + born_place[0][1] + ', ' + born_place[1] + ')'
            else:
                assert born_place[:2] == ['','']
                born_place_text = born_place[2]                
            details += 'i ' + born_place_text + '.\n\n'
        else:
            details += '(ingen uppgift om födelseort)\n\n'
        
        unknown_sex = False
        
        if len(r['civil_state']) == 2:
            assert r['civil_state'][1] in ['M', 'K']
            female = r['civil_state'][1] == 'K'
        elif r['civil_state'] in ['M', 'K']:
            female = r['civil_state'] == 'K'
        else:
            assert len(r['civil_state']) < 2
            if len(r['personal_number']) >= 11:
                female = int(r['personal_number'][10]) % 2 == 0
            else:
                unknown_sex = True
        
        if r['civil_state'] == 'M':
            civil_state = 'Man'
            assert r['civil_change'] == ''
        elif r['civil_state'] == 'K':
            civil_state = 'Kvinna'
            assert r['civil_change'] == ''
        elif r['civil_state'] == '':
            assert r['civil_change'] == ''
            years_old = self.calc_years_old(r['personal_number'], r['death_date'])
            if unknown_sex:
                assert years_old < 18
                civil_state = 'Barn under 18 år'
            elif female:
                if years_old < 18:
                    civil_state = 'Flicka under 18 år'
                else:
                    civil_state = 'Kvinna'
            else:
                if years_old < 18:
                    civil_state = 'Pojke under 18 år'
                else:
                    civil_state = 'Man'
        else:
            civil_state = int(r['civil_state'][0])
            if civil_state == 1:
                assert r['civil_change'] == ''
                years_old = self.calc_years_old(r['personal_number'], r['death_date'])
                if female:
                    if years_old < 18:
                        civil_state = 'Flicka under 18 år'
                    else:
                        civil_state = 'Ogift kvinna'
                else:
                    if years_old < 18:
                        civil_state = 'Pojke under 18 år'
                    else:
                        civil_state = 'Ogift man'
            elif civil_state == 4:
                if female:
                    civil_state = u'Frånskild kvinna' 
                else:
                    civil_state = u'Frånskild man' 
            elif civil_state == 5:
                if unknown_sex:
                    civil_state = u'Änka/Änkling'
                elif female:
                    civil_state = u'Änka'
                else:
                    civil_state = u'Änkling' 
            elif civil_state == 7:
                if female:
                    civil_state = u'Gift kvinna' 
                else:
                    civil_state = u'Gift man'
            elif civil_state == 7:
                if female:
                    civil_state = u'Efterlevande reg. partner, kvinna' 
                else:
                    civil_state = u'Efterlevande reg. partner, man'
            else:
                raise Exception(r['civil_state'])

        details += civil_state
        if r['civil_change'] != '':
            details += ' (' + self.format_date(r['civil_change']) + ')'
        details += '.\n'

        if r['notice1'] != '':
            details += '\nAnm:\n' + r['notice1'] + '\n'
        elif r['notice4'] != '':
            details += '\nAnm:\n'

        details += '--------------\n'
        
        if r['churchreg_id'] != '' and len(new_parish) != 0:
            details += 'Motsvarande kyrkobokföringsförsamling(ar) 1/1 2010:\n'
            for parish in new_parish:
                data = self.local_files['scbny_file'].search(parish + '\r', match=Match_begin, return_type=SVAR_search_return.key)
                assert len(data) == 1
                details += self.format_parish(data[0].split('\r')[1:]) + '\n'
            details += '\n'
        
        if r['born_place1'] != '':
            details += 'Födelseförsamling i källan:\n'
            details += r['born_place1'] + ' (' + born_place[0][1] + ')\n\n'
        
        details += 'Källor:\n' + r['sources'].replace('/', ' / ') + '\n'
        
        if r['notice5'] != '':
            a = []
            for x in r['notice5'].split('\r\n'):
                a.append(x.replace('Nytt dödsdatum', 'Dödsdatum', 1).replace(':', ': ', 1).replace('Dödsforskod: ', 'Dödsförsamling: Församling med SCB-kod '))
            details += '--------------\nInrapporterade rättelser: \n\n' + '\n'.join(a)


        
        return details
            
    files = {'short_data':                      {'type': 'sh190001276260ort_data',    'file_name': 'sdb5reg.i'},
             'detailed_data':                   {'type': 'detailed_data', 'file_name': 'sdb5reg.b'},
             'last_name':                       {'type': 'index',         'file_name': 'sdb5reg1.i'},
             'first_name':                      {'type': 'index',         'file_name': 'sdb5reg2.i'},
             'first_name_ordered':              {'type': 'index',         'file_name': 'sdb5reg3.i'},
             'death_date':                      {'type': 'index',         'file_name': 'sdb5reg4.i'},
             'county':                          {'type': 'index',         'file_name': 'sdb5reg5.i'}, 
             'parish':                          {'type': 'index',         'file_name': 'sdb5reg6.i'}, 
             'parish2':                         {'type': 'index',         'file_name': 'sdb5reg7.i'}, 
             'municpial':                       {'type': 'index',         'file_name': 'sdb5reg8.i'}, 
             'county':                          {'type': 'index',         'file_name': 'sdb5reg9.i'}, 
             'birth_date':                      {'type': 'index',         'file_name': 'sdb5re16.i', 'local_file_unique_keys':False},
             'test':                            {'type': 'index',         'file_name': 'sdb5re18.i'},
             'scbgam_file':                     {'type': 'data',          'file_name': 'scbgam.i', 'local_file_key_term_char':'\r', 'local_file_unique_keys':False},
             'scbny_file':                      {'type': 'data',          'file_name': 'scbny.i'},
             'foort_file':                      {'type': 'data',          'file_name': 'foort.i', 'local_file_ignore_accents': True, 'local_file_key_term_char':'\r', 'local_file_unique_keys':False}} 
        
    short_data_format = [{'name': 'detailed_data_id', 'type': 'uint32'},
                         {'type': 'uint32', 'expected': 0x90},
                         {'name': 'name', 'type': 'terminated_string', 'encode': True, 'term_char': '\r'},
                         {'name': 'birth_date', 'type': 'terminated_string'}]
    
    detailed_data_format = [{'type': 'uint32', 'expected': 0},
                            {'type': 'uint8', 'expected': 1}, {'name': 'personal_number', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'sources', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'expected': ''},
                            {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'expected': ''},
                            {'type': 'uint8', 'expected': 1}, {'name': 'name', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'postal_address', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'postal_address2', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'expected': ''},
                            {'type': 'uint8', 'expected': 1}, {'name': 'death_date', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'churchreg_year', 'type': 'terminated_string'}, #kyrkobokförd
                            {'type': 'uint8', 'expected': 1}, {'name': 'churchreg_id', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'churchreg_?', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'livingreg_year', 'type': 'terminated_string'}, #mantalskriven
                            {'type': 'uint8', 'expected': 1}, {'name': 'livingreg_id', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'livingreg_?', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'residence_year', 'type': 'terminated_string'}, #folkbokförd
                            {'type': 'uint8', 'expected': 1}, {'name': 'residence_id', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'residence_?', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'type': 'terminated_string', 'expected': ''},
                            {'type': 'uint8', 'expected': 1}, {'name': 'civil_change', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'civil_state', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'born_place2', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'born_place1', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'notice1', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'church_text', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'notice2', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'notice3', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 1}, {'name': 'notice4', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 5}, {'name': 'notice5', 'type': 'terminated_string'},
                            {'type': 'uint8', 'expected': 5}, {'name': 'notice6', 'type': 'terminated_string'},
                            {'type': 'atend'}]

    local_sub_folders = ['cdbas', 'hdbas']
    local_base_folder = 'Sveriges dödbok 1901-2009'

    def find_same(self, what, data, output):    
        if what == 'address':
            post_code = r['address2'].split('  ')
            assert len(post_code) == 2
            search_terms={'full_address': post_code[0] + ';' + data['address1'],
                          'full_address_match': Match_exact}
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
