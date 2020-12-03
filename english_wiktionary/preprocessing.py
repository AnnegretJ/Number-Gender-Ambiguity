# -*- coding: utf-8 -*-
"""
Last Updated on Sun Jul 05 18:52 2020

@author: Annegret
"""

from collections import defaultdict
from nltk.corpus import wordnet as wn
import string

def read_files():
    path = "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\wiktionaries\\"
    with open(path + "enwiktionary-new.txt",mode="r",encoding="utf-8") as data:
        # with open(path + "enwiktionary_senses_uncountable_full.txt",mode="r",encoding="utf-8") as uncountables:
            entry_dict = dict()
            for line in data:
                if line.startswith("title: "):
                    title = line[len("title: "):]
                    title = title.strip("\n")
                    if title[0].isupper():
                        continue
                    entry_dict[title] = dict()
                    entry_dict[title]["examples"] = defaultdict(list)
                    entry_dict[title]["senses"] = dict()
                # elif line.startswith("pos: ") and title in entry_dict.keys(): # check if the last value of "title" has not been deleted from the dictionary yet
                #     pos = line[len("pos: "):]
                #     pos = pos.strip("\n")
                #     if pos == "noun":
                #         entry_dict[title]["pos"] = pos
                elif line.startswith("\tplural: ") and title in entry_dict.keys():
                    plural = line[len("\tplural: "):]
                    plural = eval(plural) # convert string back to list
                    if plural == ["none"]:
                        del entry_dict[title] # remove all words without plural versions
                        continue
                    elif plural == ["unspecified"]:
                        del entry_dict[title] # remove all words with unspecified plural
                        continue
                    else:
                        entry_dict[title]["plural"] = plural
                    entry_dict[title]["plural"] = plural
                elif line.startswith("\t\tsenses") and title in entry_dict.keys():
                    index = eval(line[len("\t\tsenses")])
                    senses = line[len("\t\tsenses")+3:] # +3 for "n: " with n being number
                    # senses = eval(senses)
                    if len(senses) == 1 and senses[0].startswith("# {{plural of|en"): # remove all senses that are just "being plural of something"
                        continue
                    entry_dict[title]["senses"][index] = senses
                    # else:
                    #     for sense in senses:
                    #         uncountable_lines = uncountables.read().split("\n")
                    #         if (title + ": " + sense) in uncountable_lines:
                    #             del entry_dict[title] # remove all uncountable senses
                    #             break
                    #         entry_dict[title]["senses"] = senses
                elif line.startswith("\t\t\texamples") and title in entry_dict.keys():
                    index = eval(line[len("\t\texamples")+1])
                    examples = line[len("\t\t\texamples") + 3:] # +3 for "n: " with n being number
                    # examples = eval(examples)
                    # entry_dict[title]["examples"] = defaultdict(list)
                    # if examples != []:
                        # for sentence in examples:
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
                other.append(plural)
    return (relevant_pairs,other)

# def examples(relevant_pairs):
#     new_examples = dict() # dict for new examples, have to be added to the correct sense
#     for (singular,plural) in relevant_pairs:
#         new_examples[singular] = defaultdict(list) # so singular and plural can still be represented as one entity
#         for item in wn.synsets(singular,"n"): # find example sentences for the singular in noun classes
#             for example in item.examples():
#                 new_examples[singular][singular].append(example)
#         for item in wn.synsets(plural,"n"):
#             for example in item.examples():
#                 new_examples[singular][plural].append(example)
#     return new_examples

if __name__ == "__main__":
    entry_dict = read_files()
    relevant_pairs,other = find_pairs(entry_dict)
    # new_examples = examples(relevant_pairs)