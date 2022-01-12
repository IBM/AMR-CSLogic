from amr_verbnet_semantics.core.amr_verbnet_enhance import ground_amr
import requests

text = 'You put the wet hoodie on the patio chair.'
endpoint = f'http://128.113.12.96:5000/verbnet_semantics'  # temporary development server
# endpoint = f'http://9.116.32.235:5000/verbnet_semantics'  # temporary development server

params = {'text': text, 'use_coreference': 0}
r = requests.get(endpoint, params=params)
r = r.json()
print(r)
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
# ::tok You put the wet hoodie on the patio chair . <ROOT>
# ::node	1	you	0-1
# ::node	2	put-01	1-2
# ::node	3	wet-01	3-4
# ::node	4	hoodie	4-5
# ::node	5	patio	7-8
# ::node	6	chair	8-9
# ::root	2	put-01
# ::edge	put-01	ARG0	you	2	1	
# ::edge	hoodie	ARG1-of	wet-01	4	3	
# ::edge	put-01	ARG1	hoodie	2	4	
# ::edge	chair	mod	patio	6	5	
# ::edge	put-01	ARG2	chair	2	6	
# ::short	{1: 'y', 2: 'p', 3: 'w', 4: 'h', 5: 'p2', 6: 'c'}	
(p / put-01
      :ARG0 (y / you)
      :ARG1 (h / hoodie
            :ARG1-of (w / wet-01))
      :ARG2 (c / chair
            :mod (p2 / patio)))


***** amr_cal_str *****
[put-01(p), you(y), hoodie(h), wet-01(w), chair(c), patio(p2), put-01.arg0(p, y), put-01.arg1(p, h), wet-01.arg1(w, h), put-01.arg2(p, c), mod(c, p2)]

***** grounded_stmt_str *****
{'put.01': {'put-9.1-2': [[HAS_LOCATION(e1, Theme , Initial_Location), DO(y, e2), MOTION(ë3, h, Trajectory), NOT(HAS_LOCATION(ë3, h, Initial_Location)), HAS_LOCATION(h, c, e4), CAUSE(e2, ë3)]]}, 'wet.01': {'other_cos-45.4': [[NOT(HAS_STATE(e1, h, V_Final_State)), HAS_STATE(e2, h, V_Final_State)]]}}
'''