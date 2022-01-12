from amr_verbnet_semantics.core.amr_verbnet_enhance import ground_amr
import requests

text = 'He entered the room.'
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

print(f'\n***** pb_vn_mappings *****')
print(g_res['pb_vn_mappings'])



'''
As of 15th Oct, the output

***** amr *****
# ::tok He entered the room . <ROOT>
# ::node	1	he	0-1
# ::node	2	enter-01	1-2
# ::node	3	room	3-4
# ::root	2	enter-01
# ::edge	enter-01	ARG0	he	2	1	
# ::edge	enter-01	ARG1	room	2	3	
# ::short	{1: 'h', 2: 'e', 3: 'r'}	
(e / enter-01
      :ARG0 (h / he)
      :ARG1 (r / room))


***** amr_cal_str *****
[enter-01(e), he(h), room(r), enter-01.arg0(e, h), enter-01.arg1(e, r)]

***** grounded_stmt_str *****
{'enter.01': {'escape-51.1-2': [[MOTION(during(E), h), LOCATION(start(E), r, ?Initial_Location), LOCATION(end(E), r, ?Trajectory)]]}}

***** pb_vn_mappings *****
{'enter.01': [{'mapping': 'escape-51.1-2', 'source': 'verbnet3.4'}]}

'''