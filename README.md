# SVAR-extract

A tool to extract and search contents from SVAR databases

example:
import setup_sveriges_befolkning_1970

searches = {'last_name': '###',
            'first_name': ['###','###'],
            'birth_date': '###*'}
output = 'detailed_text_with_same_address'

res = setup_sveriges_befolkning_1970.search_and_parse(searches=searches,output=output)
print('\n'.join(res))
