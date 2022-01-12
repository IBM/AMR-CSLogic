from amr_verbnet_semantics.core.amr_verbnet_enhance import ground_amr
import requests

texts = ['The nightstand is stable.',
         'The workbench is stable.']
endpoint = f'http://9.116.32.235:5000/verbnet_semantics'  # temporary development server

for text in texts:
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
# ::tok The nightstand is stable . <ROOT>
# ::node	1	nightstand	1-2
# ::node	2	stable-03	3-4
# ::root	2	stable-03
# ::edge	stable-03	ARG1	nightstand	2	1	
# ::short	{1: 'n', 2: 's'}	
(s / stable-03
      :ARG1 (n / nightstand))


***** amr_cal_str *****
[stable-03(s), nightstand(n), stable-03.arg1(s, n)]

***** grounded_stmt_str *****
{'stable.03': {'entity_specific_cos-45.5': [[NOT(HAS_STATE(e1, Patient, V_Final_State)), HAS_STATE(Patient, e2, V_Final_State)]]}}

***** role_mappings *****
{'stable.03': {'ARG2': [{'vncls': '45.5', 'vntheta': 'patient', 'description': 'position/attribute held in equilibrium'}]}}


***** amr *****
# ::tok The workbench is stable . <ROOT>
# ::node	1	workbench	1-2
# ::node	2	stable-03	3-4
# ::root	2	stable-03
# ::edge	stable-03	ARG1	workbench	2	1	
# ::short	{1: 'w', 2: 's'}	
(s / stable-03
      :ARG1 (w / workbench))


***** amr_cal_str *****
[stable-03(s), workbench(w), stable-03.arg1(s, w)]

***** grounded_stmt_str *****
{'stable.03': {'entity_specific_cos-45.5': [[NOT(HAS_STATE(e1, Patient, V_Final_State)), HAS_STATE(Patient, e2, V_Final_State)]]}}

***** role_mappings *****
{'stable.03': {'ARG2': [{'vncls': '45.5', 'vntheta': 'patient', 'description': 'position/attribute held in equilibrium'}]}}

'''