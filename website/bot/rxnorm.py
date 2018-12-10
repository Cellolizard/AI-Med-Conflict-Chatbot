# © Copyright Mitchell Rudoll and Oliver Whittlef

import requests
import xml.etree.ElementTree as ET

URL = 'https://rxnav.nlm.nih.gov/REST/rxcui'

def rxNormId(name):
    payload = {'name' : name}
    resp = requests.get(URL, params=payload)
    if resp.status_code != 200:
        raise ApiError('GET {0} returned {1}'.format(resp.url, resp.status_code))
    xml = ET.fromstring(resp.content).findall('idGroup')[0].find('rxnormId')
    # be pythonic and return none...
    if xml is None:
        return ""
        # raise apierror('no drug named {0}'.format(name))
    return xml.text
