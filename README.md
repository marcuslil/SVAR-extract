# SVAR-extract

A tool to extract and search contents from SVAR databases

example:
from setup_sveriges_befolkning_1970 import *

search_terms = {'last_name': '###',
                'first_name': ['###','###'],
                'birth_date': '###*'}
output = 'detailed_text_with_same_address'

svbef70 = sveriges_befolkning_1970()
svbef70.set_backend_local_files()

res = svbef70.search_and_parse(search_terms=searches,output=output)
print('\n\n'.join(res))

