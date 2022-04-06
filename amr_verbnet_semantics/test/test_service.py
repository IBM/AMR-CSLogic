# Test for services

import argparse
import json
from pprint import pprint

import requests

parser = argparse.ArgumentParser()

parser.add_argument('--ip', type=str, default='0.0.0.0')
parser.add_argument('--port', type=int, default=5000)
parser.add_argument('--text', type=str, default='You enter a kitchen.')

args = parser.parse_args()

host = args.ip
port = args.port

text = args.text

res = requests.get("http://{}:{}/verbnet_semantics".format(host, port),
                   params={'text': text})

print("\nres.text:")
print(res.text)

res = json.loads(res.text)
if "amr_parse" in res:
    for i in range(len(res["amr_parse"])):
        print("\namr:")
        print(res["amr_parse"][i]["amr"])
        print("\npb_vn_mappings:")
        pprint(res["amr_parse"][i]["pb_vn_mappings"])

        print("\namr_cal:")
        print(res["amr_parse"][i]["amr_cal"])

        print("\nsem_cal:")
        print(res["amr_parse"][i]["sem_cal"])

        print("\ngrounded_stmt:")
        print(res["amr_parse"][i]["grounded_stmt"])

        print("\namr_cal:")
        print(res["amr_parse"][i]["amr_cal_str"])

        print("\nsem_cal:")
        print(res["amr_parse"][i]["sem_cal_str"])

        print("\ngrounded_stmt:")
        print(res["amr_parse"][i]["grounded_stmt_str"])
