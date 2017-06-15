#!/usr/bin/env python
import requests
import sys
from SPARQLWrapper import SPARQLWrapper, XML

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

# TODO: this can return duplicate glosses
if 'glosses' in data:
    for gloss in data['glosses']:
        if gloss['language'] == 'EN':
            print "{0}\t{1}".format(wn30id, gloss['gloss'].encode('utf-8'))


# BabelNet SPARQL endpoint has a limit on the number of calls per IP
'''
query = """
SELECT DISTINCT ?definition WHERE {
    <http://babelnet.org/rdf/"""+bnid+"""> <http://babelnet.org/model/babelnet#definition> ?gloss .
    ?gloss <http://babelnet.org/model/babelnet#gloss> ?definition .
    ?gloss <http://www.lemon-model.net/lemon#language> "EN" .
}"""
sparql = SPARQLWrapper("http://babelnet.org/sparql")
sparql.setQuery(query)
sparql.setReturnFormat(XML)
results = sparql.query().convert()
print results
xml = results.toxml()
for element in results.getElementsByTagName('binding'):
    definition = element.firstChild.firstChild.data
    print "{0}\t{1}".format(wn30id, definition.encode('utf-8'))
'''