#-*- coding: UTF-8 -*-
import re
from time import sleep
from os.path import join, dirname
from ngrams_api import runQuery

def expand_query(words_path, patterns_path):
    with open(join(dirname(__file__), words_path)) as fin:
        word_list = [x.split("\t")[1].rstrip() for x in fin.readlines()]

    with open(join(dirname(__file__), patterns_path)) as fin:
        pattern_list = [x.rstrip() for x in fin.readlines()]

    for word in word_list:
        candidates = []
        for pattern in pattern_list:
            query = pattern.replace("[lemma]", word)
            if len(query.split(" ")) > 3 and "_" in pattern:# For 4-gram and 5-gram is not possible to use POS tags in queries
                print "Part-of-speech tags can not be mixed in 4-grams or 5-grams. Invalid query:", query
            else:
                print "Processing query:", query
                candidates += runQuery(query)
                sleep(10)

        save_candidates(word, ", ".join(candidates))

def save_candidates(word, candidates):
    candidates = re.sub("_[A-Z]+", "", candidates)

    with open(join(dirname(__file__), "../data/output/query_expanded.txt"), "a") as fout:
        fout.write("%s: %s\n" % (word, candidates))

if __name__ == '__main__':  
    words_path = "../data/input/lemmas_imagenet.txt"
    patterns_path = "../data/input/patterns.txt"
    expand_query(words_path, patterns_path)
