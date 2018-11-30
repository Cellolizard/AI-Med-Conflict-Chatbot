import requests
import json

from rxnorm import *

URL = 'https://rxnav.nlm.nih.gov/REST/interaction/list.json'

def findDrugInteractions(names):
    rxcuis = map(rxNormId, names)
    # payload = {'rxcuis' : '+'.join(rxcuis) }
    # resp = requests.get(URL, params=payload)
    resp = requests.get(URL + '?rxcuis=' + '+'.join(rxcuis))
    if resp.status_code != 200:
        raise ApiError('GET {0} returned {1}'.format(resp.url, resp.status_code))
    # resp_json = json.loads(resp.json())
    print(resp.json()['fullInteractionTypeGroup'])

names = ('tylenol', 'ibuprofen', 'viagra')
findDrugInteractions(names)
