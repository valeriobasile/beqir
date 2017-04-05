#-*- coding: UTF-8 -*-
import re
from time import sleep
from os.path import join, dirname
from ngrams_api import runQuery
from prettytable import PrettyTable
from collections import Counter

def expand_query(synsets_path, patterns_path):
    synset_list, pattern_list = read_input_data(synsets_path, patterns_path)
    
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
                sleep(15)

        save_expansions(synset, word, pattern_expansions)

def save_expansions(synset, word, pattern_expansions):
    expansion_list = []
    expasion_pattern_list = []

    for pattern in pattern_expansions:
        expansions = re.sub("_[A-Z]+", "", ", ".join(pattern_expansions[pattern]))
        expasion_pattern_list.append("%s: %s" % (pattern, expansions))

        if len(expansions) > 0: expansion_list.append(expansions)

    with open(join(dirname(__file__), "../data/output/raw_data/query_expansions.txt"), "a") as fout:
        fout.write("%s\t%s\t%s\n" % (synset, word, ", ".join(expansion_list)))

    with open(join(dirname(__file__), "../data/output/raw_data/query_expansions_patterns.txt"), "a") as fout:
        fout.write("%s\t%s\t%s\n" % (synset, word, "\t".join(expasion_pattern_list)))

def read_input_data(synsets_path, patterns_path):
    synset_list = []
    pattern_list = []

    with open(join(dirname(__file__), synsets_path)) as fin:
        for line in fin:
            synset, words = line.rstrip().split("\t")
            for word in words.split(", "):
                synset_list.append((synset, word.strip()))

    with open(join(dirname(__file__), patterns_path)) as fin:
        pattern_list = [x.rstrip() for x in fin.readlines()]

    return synset_list, pattern_list

def process_data(patterns_path, expansions_path):
    all_expansions = {}
    order_data = []

    with open(join(dirname(__file__), "../data/output/raw_data/query_expansions_patterns.txt")) as fin:
        for line in fin:
            synset, word, pattern_expansion_list = read_line(line)
            if synset not in all_expansions: all_expansions[synset] = {}
            if word not in all_expansions[synset]: 
                all_expansions[synset][word] = {}
                order_data.append((synset, word))

            for pattern_expansions in pattern_expansion_list:
                pattern, expansions = pattern_expansions.split(":")
                if pattern not in all_expansions[synset][word]: all_expansions[synset][word][pattern] = set()
                expansions = [x.strip() for x in expansions.split(", ")]
                if len(expansions[0]) > 0:
                    all_expansions[synset][word][pattern].update(expansions)

    create_outputs(all_expansions, order_data, patterns_path, expansions_path)
                    
def create_outputs(all_expansions, order_data, patterns_path, expansions_path):
    single_file = []
    multiple_file = {}

    with open(join(dirname(__file__), patterns_path)) as fin:
        multiple_file = {x.rstrip():[] for x in fin.readlines()}

    for synset, word in order_data:
        expasion_pattern_list = []
        for pattern, expansions in all_expansions[synset][word].items():
            expasion_pattern_list.append("%s: %s" % (pattern, ", ".join(expansions)))
            multiple_file[pattern].append("%s\t%s\t%s" % (synset, word, ", ".join(expansions)))
        single_file.append("%s\t%s\t%s" % (synset, word, "\t".join(expasion_pattern_list)))

    with open(join(dirname(__file__), expansions_path), "w") as fout:
        fout.write("\n".join(single_file))

    for pattern in multiple_file.keys():
        with open(join(dirname(__file__), "../data/output/processed_data/%s.txt") % pattern, "w") as fout:
            fout.write("\n".join(multiple_file[pattern]))

def read_line(line):
    line_data = line.rstrip().split("\t")
    synset = line_data[0]
    word = line_data[1]
    pattern_expansion_list = line_data[2:]

    return synset, word, pattern_expansion_list

def calculate_frequent_expansions(patterns_path, expansions_path, top=10):
    expansions_frequency = {}

    with open(join(dirname(__file__), patterns_path)) as fin:
        expansions_frequency = {x.rstrip():[] for x in fin.readlines()}

    with open(join(dirname(__file__), expansions_path)) as fin:
        for line in fin:
            synset, word, pattern_expansion_list = read_line(line)
            for pattern_expansions in pattern_expansion_list:
                pattern, expansions = pattern_expansions.split(":")
                expansions = [x.strip() for x in expansions.replace(word, "").split(", ")]

                if len(expansions[0]) > 0:
                    expansions_frequency[pattern] += expansions

    for pattern in expansions_frequency.keys():
        frequencies = Counter(expansions_frequency[pattern])
        sorted_freq = sorted(frequencies.items(), key=lambda x:x[1], reverse=True)
        expansions_frequency[pattern] = [x for x,y in sorted_freq[:top]]

    return expansions_frequency

def filter_expansions(patterns_path, expansions_path):
    expansions_by_patterns = calculate_frequent_expansions(patterns_path, expansions_path)
    patterns_to_filter = ["[lemma] in the *", "[lemma] is *_VERB", "[lemma] was *_VERB"]
    frequent_expansions = []
    line_pattern_list = []

    for pattern in patterns_to_filter:
        frequent_expansions += expansions_by_patterns[pattern]

    with open(join(dirname(__file__), expansions_path)) as fin:
        for line in fin:
            synset, word, pattern_expansion_list = read_line(line)
            new_frequent_expansions = {"%s %s" % (word, x) for x in frequent_expansions}
            pattern_filtered_expansions = []

            for pattern_expansions in pattern_expansion_list:
                pattern, expansions = pattern_expansions.split(":")
                expansions = expansions.strip()
                current_filtered_expansions = []

                if len(expansions) > 0:
                    current_filtered_expansions = [x for x in expansions.split(", ") if x not in new_frequent_expansions]
                pattern_filtered_expansions.append("%s: %s" % (pattern, ", ".join(current_filtered_expansions)))
            
            line_pattern_list.append("%s\t%s\t%s" % (synset, word, "\t".join(pattern_filtered_expansions)))

    with open(join(dirname(__file__), "../data/output/filtered_data/all_expansions_filtered.txt"), "w") as fout:
        fout.write("\n".join(line_pattern_list))

def calculate_statistics(expansions_path):
    synset_dict = {}
    pattern_dict = {}

    with open(join(dirname(__file__), expansions_path)) as fin:
        for line in fin:
            synset, word, pattern_expansion_list = read_line(line)
            if synset not in synset_dict: synset_dict[synset] = {'words':[], 'expansions':[]}
            synset_dict[synset]['words'].append(word)

            for pattern_expansions in pattern_expansion_list:
                pattern, expansions = pattern_expansions.split(":")
                expansions = [x.strip() for x in expansions.split(", ")]
                if pattern not in pattern_dict: 
                    pattern_dict[pattern] = 0

                if len(expansions[0]) > 0:
                    synset_dict[synset]['expansions'] += expansions
                    pattern_dict[pattern] += len(expansions)

    print_synset_statistics(synset_dict)
    print_pattern_statistics(pattern_dict)

def print_pattern_statistics(pattern_dict):
    table = PrettyTable()
    table.field_names = ["Patterns", "Expansions"]
    table.align = "r"

    for pattern in pattern_dict:
        table.add_row([pattern, pattern_dict[pattern]])

    print table.get_string(sortby="Expansions")

def print_synset_statistics(synset_dict):
    table = PrettyTable()
    table.field_names = ["Synset", "Lemmas", "Expansions"]
    table.align = "r"

    for synset in synset_dict:
        table.add_row([synset, len(synset_dict[synset]['words']), len(set(synset_dict[synset]['expansions']))])
    
    print table.get_string(sortby="Lemmas")


if __name__ == '__main__':
    synsets_path = "../data/input/synset_imagenet.txt"
    patterns_path = "../data/input/patterns.txt"
    expansions_path = "../data/output/processed_data/all_expansions.txt"
    expand_query(synsets_path, patterns_path)
    process_data(patterns_path, expansions_path)
    filter_expansions(patterns_path, expansions_path)
    calculate_statistics("../data/output/filtered_data/all_expansions_filtered.txt")