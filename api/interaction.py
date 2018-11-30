import requests
import json

from rxnorm import *

URL = 'https://rxnav.nlm.nih.gov/REST/interaction/list.json'

# USAGE: names is a list of common drug names. Currently, just prints all of the
# interactions. This will change soon
# EXAMPLE USAGE:
#   names = ('tylenol', 'ibuprofen', 'viagra')
#   findDrugInteractions(names)

def findDrugInteractions(names):
    rxcuis = map(rxNormId, names)
    resp = requests.get(URL + '?rxcuis=' + '+'.join(rxcuis))
    if resp.status_code != 200:
        raise ApiError('GET {0} returned {1}'.format(resp.url, resp.status_code))
    for interaction_type in resp.json()['fullInteractionTypeGroup'][0]['fullInteractionType']:
        for interaction_pair in interaction_type['interactionPair']:
            print(interaction_pair['description'])
