#-*- coding: UTF-8 -*-
import re
from time import sleep
from os.path import join, dirname
from ngrams_api import runQuery
from prettytable import PrettyTable
from collections import Counter

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

def calculate_frequent_expansions(patterns_path, top=10):
    expansions_frequency = {}
    with open(join(dirname(__file__), patterns_path)) as fin:
        expansions_frequency = {x.rstrip():[] for x in fin.readlines()}

    with open(join(dirname(__file__), "../data/output/query_expanded_patterns.txt")) as fin:
        for line in fin:
            line_data = line.rstrip().split("\t")
            word = line_data[1]
            for pattern_expansions in line_data[2:]:
                pattern_expansions = pattern_expansions.split(":")
                pattern = pattern_expansions[0]
                expansions = [x.strip() for x in pattern_expansions[1].replace(word, "").split(",")]
                if len(expansions[0]) > 0:
                    expansions_frequency[pattern] += expansions

    for pattern in expansions_frequency.keys():
        frequencies = Counter(expansions_frequency[pattern])
        sorted_freq = sorted(frequencies.items(), key=lambda x:x[1], reverse=True)
        expansions_frequency[pattern] = [x for x,y in sorted_freq[:top]]

    return expansions_frequency

def filter_expansions(patterns_path):
    expansions_by_patterns = calculate_frequent_expansions(patterns_path)
    patterns_to_filter = ["[lemma] in the *", "[lemma] is *_VERB", "[lemma] was *_VERB"]
    frequent_expansions = []
    line_list = []

    for pattern in patterns_to_filter:
        frequent_expansions += expansions_by_patterns[pattern]

    with open(join(dirname(__file__), "../data/output/query_expanded.txt")) as fin:
        for line in fin:
            synset, word, expansions = line.split("\t")
            expansions = expansions.rstrip()
            new_frequent_expansions = {"%s %s" % (word, x) for x in frequent_expansions}
            filtered_expansions = [x for x in expansions.split(", ") if x not in new_frequent_expansions]
            line_list.append("%s\t%s\t%s" % (synset, word, ", ".join(filtered_expansions)))

    with open(join(dirname(__file__), "../data/output/query_expanded_filtered.txt"), "w") as fout:
        fout.write("\n".join(line_list))


if __name__ == '__main__':
    synsets_path = "../data/input/synset_imagenet.txt"
    patterns_path = "../data/input/patterns.txt"
    expand_query(synsets_path, patterns_path)
    calculate_synset_statistics()
    filter_expansions(patterns_path)