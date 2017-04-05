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

def process_expansions(patterns_path, output_folder):
    all_expansions = {}
    order_expansions = []
    patterns = []

    with open(join(dirname(__file__), patterns_path)) as fin:
        patterns =[x.rstrip() for x in fin.readlines()]

    with open(join(dirname(__file__), "../data/output/raw_data/query_expansions_patterns.txt")) as fin:
        for line in fin:
            synset, word, pattern_expansion_list = read_line(line)
            if synset not in all_expansions: all_expansions[synset] = {}
            if word not in all_expansions[synset]: 
                all_expansions[synset][word] = {}
                order_expansions.append((synset, word))

            for pattern_expansions in pattern_expansion_list:
                pattern, expansions = pattern_expansions.split(":")
                if pattern not in all_expansions[synset][word]: all_expansions[synset][word][pattern] = set()
                expansions = [x.strip() for x in expansions.split(", ")]
                if len(expansions[0]) > 0:
                    all_expansions[synset][word][pattern].update(expansions)

    expansions_data = {'all_expansions':all_expansions, 'order_expansions':order_expansions, 'patterns':patterns}
    create_outputs(expansions_data, output_folder)

    return expansions_data
                    
def filter_expansions(expansions_data, output_folder):
    frequent_expansions = calculate_frequent_expansions(expansions_data)
    patterns_to_filter = {"[lemma] in the *", "[lemma] is *_VERB", "[lemma] was *_VERB"}

    for synset, words_data in expansions_data['all_expansions'].items():
        for word, patterns_data in expansions_data['all_expansions'][synset].items():
            for pattern, expansions in expansions_data['all_expansions'][synset][word].items():
                if pattern in patterns_to_filter:
                    new_frequent_expansions = {"%s %s" % (word, x) for x in frequent_expansions[pattern]}
                    filtered_expansions = {x for x in expansions if x not in new_frequent_expansions}
                    expansions_data['all_expansions'][synset][word][pattern] = filtered_expansions

    create_outputs(expansions_data, output_folder)

def calculate_frequent_expansions(expansions_data, top=10):
    expansions_frequency = {x.rstrip():[] for x in expansions_data['patterns']}

    with open(join(dirname(__file__), "../data/output/processed_data/all_expansions.txt")) as fin:
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

def create_outputs(expansions_data, output_folder):
    all_expansions = expansions_data['all_expansions']
    order_expansions = expansions_data['order_expansions']
    patterns = expansions_data['patterns']
    single_file = []
    multiple_file = {x:[] for x in patterns}

    for synset, word in order_expansions:
        expasion_pattern_list = []
        for pattern, expansions in all_expansions[synset][word].items():
            expasion_pattern_list.append("%s: %s" % (pattern, ", ".join(expansions)))
            multiple_file[pattern].append("%s\t%s\t%s" % (synset, word, ", ".join(expansions)))
        single_file.append("%s\t%s\t%s" % (synset, word, "\t".join(expasion_pattern_list)))

    with open(join(dirname(__file__), "%s/all_expansions.txt") % output_folder, "w") as fout:
        fout.write("\n".join(single_file))

    for index, pattern in enumerate(patterns):
        with open(join(dirname(__file__), "%s/pattern_%d.txt") % (output_folder, index+1), "w") as fout:
            fout.write("\n".join(multiple_file[pattern]))

    with open(join(dirname(__file__), "%s/pattern_names.txt") % output_folder, "w") as fout:
        fout.write("\n".join(["pattern_%d: %s" % (i+1, x) for i,x in enumerate(patterns)]))      

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

def read_line(line):
    line_data = line.rstrip().split("\t")
    synset = line_data[0]
    word = line_data[1]
    pattern_expansion_list = line_data[2:]

    return synset, word, pattern_expansion_list

if __name__ == '__main__':
    synsets_path = "../data/input/synset_imagenet.txt"
    patterns_path = "../data/input/patterns.txt"
    processed_data_folder = "../data/output/processed_data/"
    filtered_data_folder = "../data/output/filtered_data/"
    #expand_query(synsets_path, patterns_path)
    expansions_data = process_expansions(patterns_path, processed_data_folder)
    filter_expansions(expansions_data, filtered_data_folder)
    calculate_statistics("../data/output/filtered_data/all_expansions.txt")