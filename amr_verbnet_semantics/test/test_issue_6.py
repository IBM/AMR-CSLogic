from amr_verbnet_semantics.core.amr_verbnet_enhance import ground_amr
import requests

text = 'The dresser is made out of maple carefully finished with Danish oil.'
endpoint = f'http://9.116.32.235:5000/verbnet_semantics'  # temporary development server

params = {'text': text, 'use_coreference': 0}
r = requests.get(endpoint, params=params)
r = r.json()
amr = r['amr_parse'][0]['amr']
amr_cal_str = r['amr_parse'][0]['amr_cal_str']


print(f'***** amr *****')
print(amr)
print(f'***** amr_cal_str *****')
print(amr_cal_str)

g_res = ground_amr(amr)
print(f'\n***** grounded_stmt_str *****')
print(g_res['grounded_stmt_str'])

print(f'\n***** role_mappings *****')
print(g_res['role_mappings'])
print('\n')



'''
As of 15th Oct, the output

***** amr *****
# ::tok The dresser is made out of maple carefully finished with Danish oil . <ROOT>
# ::node	1	dresser	1-2
# ::node	2	make-01	3-4
# ::node	3	maple	6-7
# ::node	4	careful	7-8
# ::node	5	finish-01	8-9
# ::node	6	country	10-11
# ::node	8	oil	11-12
# ::node	9	"Denmark"	10-11
# ::node	11	name	10-11
# ::root	2	make-01
# ::edge	make-01	ARG1	dresser	2	1	
# ::edge	make-01	ARG2	maple	2	3	
# ::edge	finish-01	manner	careful	5	4	
# ::edge	maple	ARG1-of	finish-01	3	5	
# ::edge	oil	mod	country	8	6	
# ::edge	finish-01	ARG2	oil	5	8	
# ::edge	country	name	name	6	11	
# ::edge	name	op1	"Denmark"	11	9	
# ::short	{1: 'd', 2: 'm', 3: 'm2', 4: 'c', 5: 'f', 6: 'c2', 8: 'o', 9: 'x0', 11: 'n'}	
(m / make-01
      :ARG1 (d / dresser)
      :ARG2 (m2 / maple
            :ARG1-of (f / finish-01
                  :ARG2 (o / oil
                        :mod (c2 / country
                              :name (n / name
                                    :op1 "Denmark")))
                  :manner (c / careful))))


***** amr_cal_str *****
[make-01(m), dresser(d), maple(m2), finish-01(f), oil(o), country(c2), name(n), careful(c), make-01.arg1(m, d), make-01.arg2(m, m2), finish-01.arg1(f, m2), finish-01.arg2(f, o), mod(o, c2), name(c2, n), manner(f, c)]

***** grounded_stmt_str *****
{'make.01': {'build-26.1-1': [[NOT(BE(d, e1)), DO(e2, Agent), BE(e3, d), MADE_OF(e3, d, m2), CAUSE(e2, e3), COST(E, d, Asset)]]}, 'finish.01': {'stop-55.4-1': [[END(E, m2)]]}}

***** role_mappings *****
{'make.01': {'ARG0': [{'vncls': '26.1-1', 'vntheta': 'agent', 'description': 'creator'}], 'ARG1': [{'vncls': '26.1-1', 'vntheta': 'product', 'description': 'creation'}], 'ARG2': [{'vncls': '26.1-1', 'vntheta': 'material', 'description': 'created-from, thing changed'}], 'ARG3': [{'vncls': '26.1-1', 'vntheta': 'beneficiary', 'description': 'benefactive'}]}, 'finish.01': {'ARG1': [{'vncls': '55.4-1', 'vntheta': 'theme', 'description': 'Thing finishing'}]}}

'''