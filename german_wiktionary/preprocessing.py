# -*- coding: utf-8 -*-
"""
Last Updated on Sun Jul 06 16:50 2020

@author: Annegret
"""

from collections import defaultdict
from nltk.corpus import wordnet as wn
import string

def read_files():
    path = "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\german_wiktionary\\wiktionaries\\"
    # path = "/home/tili/Documents/DFKI/MLT/gewiktionary/"
    with open(path + "enwiktionary-new1.txt",mode="r",encoding="utf-8") as data:
        entry_dict = dict()
        for line in data:
            if line.startswith("title: "):
                title = line[len("title: "):]
                title = title.strip("\n")
                if title[0].isupper():
                    continue
                entry_dict[title] = dict()
            elif line.startswith("pos: ") and title in entry_dict.keys(): # check if the last value of "title" has not been deleted from the dictionary yet
                pos = line[len("pos: "):]
                pos = pos.strip("\n")
                if pos == "noun":
                    entry_dict[title]["pos"] = pos
            elif line.startswith("genus: ") and title in entry_dict.keys():
                genus = line[len("genus: "):]
                genus = eval(genus) # convert string back to list
                if genus == []:
                    del entry_dict[title] # remove all words without genus
                    continue
                else:
                    entry_dict[title]["genus"] = genus
            elif line.startswith("senses: ") and title in entry_dict.keys():
                senses = line[len("senses: "):]
                senses = eval(senses)
                entry_dict[title]["senses"] = defaultdict(list)
                for genus,sense in senses:
                    entry_dict[title]["senses"][genus].append(sense)
            elif line.startswith("examples: ") and title in entry_dict.keys():
                examples = line[len("examples: "):]
                examples = eval(examples)
                entry_dict[title]["examples"] = defaultdict(list)
                if examples != []:
                    for sense,sentence in examples:
                        sentence = sentence.translate(str.maketrans('', '', string.punctuation)) # remove all punctuation
                        entry_dict[title]["examples"][sense].append(sentence)
    return entry_dict

def find_words(entry_dict):
    relevant_words = [] # list of all words with different genus depending on meaning
    for title in entry_dict.keys():
        if len(entry_dict[title]["senses"].keys()) > 1: # when there is more than one possible genus
            relevant_words.append(title)
    return relevant_words

def examples(relevant_words):
    new_examples = defaultdict(list) # dict for new examples, have to be added to the correct sense
    for word in relevant_words:
        for item in wn.synsets(word,"n"): # find example sentences for the singular in noun classes
            for example in item.examples():
                new_examples[word].append(example)
    return new_examples

if __name__ == "__main__":
    entry_dict = read_files()
    relevant_words = find_words(entry_dict)
    new_examples = examples(relevant_words)