#!/usr/bin/env python
import requests
import sys

BNKEY='b516da18-da20-482c-be32-44c1692ed9be'

# process input
pos = sys.argv[1][0]
wn30id = sys.argv[1][1:]+'-'+pos

wn31id = None
with open('wn30-31') as f:
    for line in f:
        wn30, wn31 = line.rstrip().split(' ')
        if wn30 == wn30id:
            wn31id = wn31

if wn31id == None:
    sys.exit(0)

bnid = None
with open("bn35-wn31.map") as f:
    for line in f:
        bn, senseid, wn31 = line.rstrip().split(' ')
        if wn31[1:] == wn31id:
            bnid = bn.replace('s', 'bn:')

if bnid == None:
    sys.exit(0)

args = {'id': bnid, 'key': BNKEY}
r = requests.get('https://babelnet.io/v4/getSynset', args)
data = r.json()

if 'lnToCompound' in data:
    if 'EN' in data['lnToCompound']:
        compounds = data['lnToCompound']['EN']
        for compound in compounds:
            print "{0}\t{1}".format(wn30id, compound.replace('_', ' ').encode('utf-8'))
