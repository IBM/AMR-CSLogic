from amr_verbnet_semantics.core.amr_verbnet_enhance import ground_amr
import requests

text = 'wet hoodie'
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

'''
As of 15th Oct, the output

***** amr *****
# ::tok wet hoodie <ROOT>
# ::node	1	wet-01	0-1
# ::node	2	hoodie	1-2
# ::root	2	hoodie
# ::edge	hoodie	ARG1-of	wet-01	2	1	
# ::short	{1: 'w', 2: 'h'}	
(h / hoodie
      :ARG1-of (w / wet-01))


***** amr_cal_str *****
[hoodie(h), wet-01(w), wet-01.arg1(w, h)]

***** grounded_stmt_str *****
{'wet.01': {'other_cos-45.4': [[NOT(HAS_STATE(e1, h, V_Final_State)), HAS_STATE(e2, h, V_Final_State)]]}}
'''