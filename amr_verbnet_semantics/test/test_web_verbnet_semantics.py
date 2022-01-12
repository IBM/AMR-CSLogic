import requests

from app_config import config

if __name__ == '__main__':

    text = 'The dresser is made out of maple carefully finished with Danish oil'
    params = {'text': text, 'use_coreference': 0}
    endpoint = f'http://{config.LOCAL_SERVICE_HOST}:{config.LOCAL_SERVICE_PORT}/verbnet_semantics'
    r = requests.get(endpoint, params=params)
    print(r.json())
