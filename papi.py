import requests
import ujson
from requests.auth import HTTPDigestAuth


class Papi(object):
    def __init__(self):
        self.cache = {}

    def get_url(self, url):
        if not url in self.cache:
            resp = requests.get(papify(url),  auth=HTTPDigestAuth('human', 'R3plicant')).text
            if not resp:
                self.cache[url] = False

            data = ujson.loads(resp)
            if not data['status'] == 'ERROR' and not data['type'] == 'redirect' and 'result' in data:
                self.cache[url] = True
            else:
                self.cache[url] = False

        return self.cache[url]

class Tagger(object):
    def __init__(self):
        self.cache = {}

    def get_tags(self, url):
        if not url in self.cache:
            resp = requests.get(papify(url),  auth=HTTPDigestAuth('human', 'R3plicant')).text
            if not resp:
                self.cache[url] = False

            data = ujson.loads(resp)
            if not data['status'] == 'ERROR' and not data['type'] == 'redirect' and 'result' in data:
                self.cache[url] = data['result']['catalogue_keywords']
            else:
                self.cache[url] = False

        return self.cache[url]

def papify(url):
    papi = 'http://cms-publishapi.prd.nytimes.com/v1/publish/scoop/'
    return papi + url.split('.com/')[1].split('?')[0]