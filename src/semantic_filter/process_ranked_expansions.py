#!/usr/bin/env python
from math import ceil

expansions = dict()
with open('ranked_query_expansions.tsv') as f:
    for line in f:
        relevance, synsetid, expansion = line[:-1].split('\t')
        relevance = eval(relevance)
        synsetid = synsetid[1:-1]
        expansion = expansion[1:-1]
        if not synsetid in expansions:
            expansions[synsetid] = []
        expansions[synsetid].append((relevance, expansion))

for synsetid in expansions:
    l = len(expansions[synsetid])
    print synsetid
    for i in range(4):
        fraction = float(i+1)/4.0
        label = str(int(fraction*100))
        topn = int(ceil(l*fraction))
        print l, label, topn
        with open('topn/query_expansions_{0}.tsv'.format(label), 'a') as f:
            for (relevance, expansion) in expansions[synsetid][:topn+1]:
                f.write('{0}\t{1}\n'.format(synsetid, expansion))
