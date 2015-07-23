import requests
import json
from requests.auth import HTTPDigestAuth

def get_tags(url):
    resp = requests.get(papify(url),  auth=HTTPDigestAuth('human', 'R3plicant')).text
    if not resp:
        return None

    papi = json.loads(resp)
    if papi and not papi['status'] == 'ERROR' and not papi['type'] == 'redirect':
        try:
            tags = papi['result']['catalogue_keywords']
        except Exception as e:
            print(papi)


def papify(url):
    papi = 'http://cms-publishapi.prd.nytimes.com/v1/publish/scoop/'
    return papi + url.split('.com/')[1].split('?')[0]