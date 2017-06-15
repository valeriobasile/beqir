#!/usr/bin/env python

queryexpansions = dict()
for i in range(1, 6):
    with open('pattern_{0}.txt'.format(i)) as f:
        for line in f:
            synsetid, lemma, expansionlist = line[:-1].split('\t')
            key = (synsetid, lemma)
            if key not in queryexpansions:
                queryexpansions[key] = []
            if expansionlist != '':
                queryexpansions[key].extend(expansionlist.split(', '))

for (synsetid, lemma), expansions in queryexpansions.iteritems():
    print "{0}\t{1}\t{2}".format(synsetid, lemma, ', '.join(expansions))
