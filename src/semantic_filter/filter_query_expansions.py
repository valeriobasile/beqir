#!/usr/bin/env python

from gensim.models.keyedvectors import KeyedVectors
import logging as log
from nltk import word_tokenize
import random
from itertools import product

MODEL_FILE = 'GoogleNews-vectors-negative300.bin'

log.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=log.INFO)

model = KeyedVectors.load_word2vec_format(MODEL_FILE, binary=True)

def similarity(w1, w2):
    if not w1.lower() in model:
        log.warning('word not found in the model: {0}'.format(w1))
        return 0.0
    if not w2.lower() in model:
        log.warning('word not found in the model: {0}'.format(w2))
        return 0.0
    try:
        return model.similarity(w1, w2)
    except:
        log.warning('error computing the similarities between words {0} and {1}'.format(w1, w2))
'''
# bogus function
def similarity(w1, w2):
    return random.random()
'''
def sentence_similarity(lemmalist, s1, s2):
    sim = 0.0
    wl1 = word_tokenize(s1)
    wl2 = word_tokenize(s2)
    pairs = list(product(wl1, wl2))
    i = 0.0
    for w1, w2 in pairs:
        if not w1 in lemmalist:
            sim += similarity(w1.lower(), w2.lower())
            i+=1.0
    if i == 0.0:
        return 0.0
    else:
        return sim/i

def composite_similarity(lemmalist, input_phrase, target_list):
    sim = 0.0
    for target in target_list:
        sim += sentence_similarity(lemmalist, input_phrase, target)
    return sim / float(len(target_list))

log.info('reading synset definitions')
definitions = dict()
with open('definitions.tsv') as f:
    for line in f:
        synsetid, definition = line.rstrip().split('\t')
        if not synsetid in definitions:
            definitions[synsetid] = []
        definitions[synsetid].append(definition)

log.info('reading input synsets')
expansions = dict()
lemmas = dict()
with open('query_expansions.txt') as f:
    for line in f:
        synsetid, lemmalist, expansionlist = line[:-1].split('\t')
        if not synsetid in expansions:
            expansions[synsetid] = []
        expansions[synsetid].extend(expansionlist.split(', '))
        if not synsetid in lemmas:
            lemmas[synsetid] = []
        lemmas[synsetid].extend(lemmalist.rstrip().split(', '))

for synsetid, expansionlist in expansions.iteritems():
    if synsetid in definitions:
        for expansion in expansionlist:
            score = composite_similarity(lemmas[synsetid], expansion, definitions[synsetid])
            print "{0}\t{1}\t{2}".format(score, synsetid, expansion)
