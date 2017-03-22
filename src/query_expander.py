#-*- coding: UTF-8 -*-
import re
from time import sleep
from os.path import join, dirname
from ngrams_api import runQuery
from prettytable import PrettyTable

def expand_query(synsets_path, patterns_path):
    synset_list, pattern_list = read_data(synsets_path, patterns_path)
    
    for synset, word in synset_list:
        candidates = []
        for pattern in pattern_list:
            query = pattern.replace("[lemma]", word)
            if len(query.split(" ")) > 3 and "_" in pattern:# For 4-gram and 5-gram is not possible to use POS tags in queries
                print "Part-of-speech tags can not be mixed in 4-grams or 5-grams. Invalid query:", query
            else:
                print "Processing query:", query
                candidates += runQuery(query)
                sleep(10)

        save_candidates(synset, word, ", ".join(candidates))

def save_candidates(synset, word, candidates):
    candidates = re.sub("_[A-Z]+", "", candidates)

    with open(join(dirname(__file__), "../data/output/query_expanded.txt"), "a") as fout:
        fout.write("%s\t%s\t%s\n" % (synset, word, candidates))

def read_data(synsets_path, patterns_path):
    synset_list = []
    pattern_list = []

    with open(join(dirname(__file__), synsets_path)) as fin:
        for line in fin:
            line_data = line.split("\t")
            synset = line_data[0]
            for word in line_data[1].split(","):
                synset_list.append((synset, word.strip()))

    with open(join(dirname(__file__), patterns_path)) as fin:
        pattern_list = [x.rstrip() for x in fin.readlines()]

    return synset_list, pattern_list

def calculate_statistics():
    synset_dict = {}
    table = PrettyTable()
    table.field_names = ["Synset", "Lemmas", "Expanded Lemmas"]
    table.align = "r"

    with open(join(dirname(__file__), "../data/output/query_expanded.txt")) as fin:
        for line in fin:
            line_data = line.rstrip().split("\t")
            synset = line_data[0]
            word = line_data[1]
            expanded_words = line_data[2].split(", ") if len(line_data) > 2 else []
            
            if synset not in synset_dict: synset_dict[synset] = {'words':[], 'expanded_words':[]}
            synset_dict[synset]['words'].append(word)
            synset_dict[synset]['expanded_words'] += expanded_words

    for synset in synset_dict:
        table.add_row([synset, len(synset_dict[synset]['words']), len(set(synset_dict[synset]['expanded_words']))])
    
    print table.get_string(sortby="Lemmas")

if __name__ == '__main__':
    synsets_path = "../data/input/synset_imagenet_10.txt"
    patterns_path = "../data/input/patterns.txt"
    #expand_query(synsets_path, patterns_path)
    calculate_statistics()
