import requests
import ujson, os
from requests.auth import HTTPDigestAuth
import cPickle as pickle


class Papi(object):
    def __init__(self):
        self.cache = {}

    def get_url(self, url):
        if not url in self.cache:
            resp = requests.get(papify(url),  auth=HTTPDigestAuth('human', 'R3plicant')).text
            if not resp:
                self.cache[url] = False

            data = ujson.loads(resp)
            if not data['status'] == 'ERROR' and 'result' in data and 'data_type' in data['result'] and data['result']['data_type'] == 'article':
                self.cache[url] = True
            else:
                self.cache[url] = False
        else:
            print('cache hit')
        return self.cache[url]

class Tagger(object):
    def __init__(self):
        self.cache = {}
        if os.path.exists('cache.pkl'):
            self.load_cache()
        #print self.cache

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

    def load_cache(self,fn='cache.pkl'):
        with open(fn,'rb') as f:
            self.cache = pickle.load(f)

    def write_cache(self,fn='cache.pkl'):
        with open(fn,'wb') as f:
            pickle.dump(self.cache,f)


def papify(url):
    papi = 'http://cms-publishapi.prd.nytimes.com/v1/publish/scoop/'
    return papi + url.split('.com/')[1].split('?')[0]