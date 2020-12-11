# -*- coding: utf-8 -*-
"""
Last Updated on Sun Jul 05 18:52 2020

@author: Annegret
"""

from collections import defaultdict
from nltk.corpus import wordnet as wn
import string
from tqdm import tqdm

def read_files(filename):
    with open(filename,mode="r",encoding="utf-8") as data:
        entry_dict = dict()
        for line in data:
            if line.startswith("title: "):
                title = line[len("title: "):]
                title = title.strip("\n")
                if title[0].isupper():
                    continue
                if title not in entry_dict.keys():
                    entry_dict[title] = dict()
                    entry_dict[title]["examples"] = defaultdict(list)
                    entry_dict[title]["senses"] = dict()
            elif line.startswith("\tplural: ") and title in entry_dict.keys():
                plural = line[len("\tplural: "):]
                plural = eval(plural) # convert string back to list
                if plural == ["none"]:
                    del entry_dict[title] # remove all words without plural versions
                    continue
                elif plural == ["unspecified"]:
                    del entry_dict[title] # remove all words with unspecified plural
                    continue
                if "plural" not in entry_dict[title].keys():
                    entry_dict[title]["plural"] = plural
                else:
                    for item in plural:
                        if item not in entry_dict[title]["plural"]:
                            entry_dict[title]["plural"].append(item)
            elif line.startswith("\t\tsenses") and title in entry_dict.keys():
                index = eval(line[len("\t\tsenses")])
                senses = line[len("\t\tsenses")+3:] # +3 for "n: " with n being number
                if len(senses) == 1 and senses[0].startswith("# {{plural of|en"): # remove all senses that are just "being plural of something"
                    continue
                entry_dict[title]["senses"][index] = senses
            elif line.startswith("\t\t\texamples") and title in entry_dict.keys():
                index = eval(line[len("\t\texamples")+1])
                examples = line[len("\t\t\texamples") + 3:] # +3 for "n: " with n being number
                examples = examples.translate(str.maketrans('', '', string.punctuation)) # remove all punctuation
                entry_dict[title]["examples"][index].append(examples)
    return entry_dict

def find_pairs(entry_dict):
    relevant_pairs = [] # list of singulars and plurals with own sense
    other = []
    for title in entry_dict.keys():
        plural = entry_dict[title]["plural"]
        for item in plural:
            if item == "none": # only use existing plurals
                other.append(title)
                continue
            if item in entry_dict.keys() and entry_dict[item] != entry_dict[title]: # when plural has an own entry, which is not the current entry (when plural is written the same as singular)
                relevant_pairs.append((title,item)) # add all pairs of singular and plural with own sense to list
            else:
                other.append(title)
    return (relevant_pairs,other)

if __name__ == "__main__":
    path = "wiktionaries\\"
    filename = path + "enwiktionary-new.txt"
    entry_dict = read_files(filename)
    relevant_pairs,other = find_pairs(entry_dict)
