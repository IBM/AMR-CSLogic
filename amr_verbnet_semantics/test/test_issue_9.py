from amr_verbnet_semantics.core.amr_verbnet_enhance import ground_amr
import requests

texts = ['On the nightstand is a clean red dress.',
         'On the chair is a hoodie.',
         'The bench is shaky.']
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
    print('\n')

'''
As of 15th Oct, the output

***** amr *****
# ::tok On the nightstand is a clean red dress . <ROOT>
# ::node	1	nightstand	2-3
# ::node	2	clean-04	5-6
# ::node	3	red-02	6-7
# ::node	4	dress	7-8
# ::root	4	dress
# ::edge	dress	ARG1-of	red-02	4	3	
# ::edge	dress	ARG1-of	clean-04	4	2	
# ::edge	dress	location	nightstand	4	1	
# ::short	{1: 'n', 2: 'c', 3: 'r', 4: 'd'}	
(d / dress
      :ARG1-of (r / red-02)
      :ARG1-of (c / clean-04)
      :location (n / nightstand))


***** amr_cal_str *****
[dress(d), red-02(r), clean-04(c), nightstand(n), red-02.arg1(r, d), clean-04.arg1(c, d), location(d, n)]

***** grounded_stmt_str *****
{}


***** amr *****
# ::tok On the chair is a hoodie . <ROOT>
# ::node	1	be-located-at-91	0-1
# ::node	2	chair	2-3
# ::node	3	hoodie	5-6
# ::root	1	be-located-at-91
# ::edge	be-located-at-91	ARG2	chair	1	2	
# ::edge	be-located-at-91	ARG1	hoodie	1	3	
# ::short	{1: 'b', 2: 'c', 3: 'h'}	
(b / be-located-at-91
      :ARG1 (h / hoodie)
      :ARG2 (c / chair))


***** amr_cal_str *****
[be-located-at-91(b), hoodie(h), chair(c), be-located-at-91.arg1(b, h), be-located-at-91.arg2(b, c)]

***** grounded_stmt_str *****
{}


***** amr *****
# ::tok The bench is shaky . <ROOT>
# ::node	1	bench	1-2
# ::node	2	shaky	3-4
# ::root	2	shaky
# ::edge	shaky	domain	bench	2	1	
# ::short	{1: 'b', 2: 's'}	
(s / shaky
      :domain (b / bench))


***** amr_cal_str *****
[shaky(s), bench(b), domain(s, b)]

***** grounded_stmt_str *****
{}


'''