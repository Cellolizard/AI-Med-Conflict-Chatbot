import requests
import json

from .rxnorm import *

URL = 'https://rxnav.nlm.nih.gov/REST/interaction/list.json'

# USAGE: names is a list of common drug names. Currently, just prints all of the
# interactions. This will change soon
# EXAMPLE USAGE:
#   names = ('tylenol', 'ibuprofen', 'viagra')
#   findDrugInteractions(names)

def findDrugInteractions(rxcuis):
    rxcuis = filter(None, rxcuis)
    resp = requests.get(URL + '?rxcuis=' + '+'.join(rxcuis))
    interactions = {}
    if resp.status_code != 200:
        raise ApiError('GET {0} returned {1}'.format(resp.url, resp.status_code))
    for interaction_type in resp.json()['fullInteractionTypeGroup'][0]['fullInteractionType']:
        for interaction_pair in interaction_type['interactionPair']:
            d1 = interaction_type['minConcept'][0]['rxcui']
            d2 = interaction_type['minConcept'][1]['rxcui']
            interactions['{0},{1}'.format(d1, d2)] = interaction_pair['description']
    return interactions

# TEST:
# names = ('tylenol', 'ibuprofen', 'viagra')
# print(findDrugInteractions(map(rxNormId, names)))
