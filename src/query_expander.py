#-*- coding: UTF-8 -*-
import re
from time import sleep
from os.path import join, dirname
from ngrams_api import runQuery
from prettytable import PrettyTable

def expand_query(synsets_path, patterns_path):
    synset_list, pattern_list = read_data(synsets_path, patterns_path)
    pattern_track = {x:0 for x in pattern_list}
    
    for synset, word in synset_list:
        pattern_expansions = {}
        for pattern in pattern_list:
            pattern_expansions[pattern] = []
            query = pattern.replace("[lemma]", word)
            if len(query.split(" ")) > 3 and "_" in pattern:# For 4-gram and 5-gram is not possible to use POS tags in queries
                print "Part-of-speech tags can not be mixed in 4-grams or 5-grams. Invalid query:", query
            else:
                print "Processing query:", query
                pattern_expansions[pattern] = runQuery(query)
                pattern_track[pattern] += len(pattern_expansions[pattern])
                sleep(10)

        save_expansions(synset, word, pattern_expansions)
    calculate_pattern_statistics(pattern_track)

def save_expansions(synset, word, pattern_expansions):
    expansion_list = []
    expasion_pattern_list = []

    for pattern in pattern_expansions:
        expansions = re.sub("_[A-Z]+", "", ", ".join(pattern_expansions[pattern]))
        expasion_pattern_list.append("%s: %s" % (pattern, expansions))
        if len(expansions) > 0: expansion_list.append(expansions)

    with open(join(dirname(__file__), "../data/output/query_expanded.txt"), "a") as fout:
        fout.write("%s\t%s\t%s\n" % (synset, word, ", ".join(expansion_list)))

    with open(join(dirname(__file__), "../data/output/query_expanded_patterns.txt"), "a") as fout:
        fout.write("%s\t%s\t%s\n" % (synset, word, "\t".join(expasion_pattern_list)))

def read_data(synsets_path, patterns_path):
    synset_list = []
    pattern_list = []

    with open(join(dirname(__file__), synsets_path)) as fin:
        for line in fin:
            line_data = line.rstrip().split("\t")
            synset = line_data[0]
            for word in line_data[1].split(", "):
                synset_list.append((synset, word.strip()))

    with open(join(dirname(__file__), patterns_path)) as fin:
        pattern_list = [x.rstrip() for x in fin.readlines()]

    return synset_list, pattern_list

def calculate_pattern_statistics(pattern_track):
    table = PrettyTable()
    table.field_names = ["Patterns", "Expansions"]
    table.align = "r"

    for pattern in pattern_track:
        table.add_row([pattern, pattern_track[pattern]])

    print table.get_string(sortby="Expansions")

def calculate_synset_statistics():
    synset_dict = {}
    table = PrettyTable()
    table.field_names = ["Synset", "Lemmas", "Expansions"]
    table.align = "r"

    with open(join(dirname(__file__), "../data/output/query_expanded.txt")) as fin:
        for line in fin:
            line_data = line.rstrip().split("\t")
            synset = line_data[0]
            word = line_data[1]
            expansions = line_data[2].split(", ") if len(line_data) > 2 else []
            
            if synset not in synset_dict: synset_dict[synset] = {'words':[], 'expansions':[]}
            synset_dict[synset]['words'].append(word)
            synset_dict[synset]['expansions'] += expansions

    for synset in synset_dict:
        table.add_row([synset, len(synset_dict[synset]['words']), len(set(synset_dict[synset]['expansions']))])
    
    print table.get_string(sortby="Lemmas")

if __name__ == '__main__':
    synsets_path = "../data/input/synset_imagenet_10.txt"
    patterns_path = "../data/input/patterns.txt"
    expand_query(synsets_path, patterns_path)
    calculate_synset_statistics()
