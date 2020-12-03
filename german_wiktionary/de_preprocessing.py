# -*- coding: utf-8 -*-
"""
Last Updated on Mon Sep 17 16:20 2020

@author: Annegret
"""

from collections import defaultdict
# from nltk.corpus import wordnet as wn
import string

def read_files():
    path = "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\german_wiktionary\\wiktionaries\\"
    with open(path + "dewiktionary-new.txt",mode="r",encoding="utf-8") as data:
        with open("Ausnahmen.txt",mode="w+",encoding="utf-8") as ausnahmen:
            entry_dict = defaultdict()
            for line in data:
                if line.startswith("title: "):
                    title = line[len("title: "):]
                    title = title.strip("\n")
                    entry_dict[title] = defaultdict(set)
                    entry_dict[title]["examples"] = defaultdict(set)
                    entry_dict[title]["senses"] = dict()
                elif line.startswith("\tgender: ") and title in entry_dict.keys(): # genus = gender
                    genus = line[len("\tgender: "):]
                    genus = eval(genus)
                    for item in genus:
                        entry_dict[title]["senses"][item] = dict()
                        entry_dict[title]["gender"].add(item)
                elif line.startswith("\tplural: ") and title in entry_dict.keys():
                    plural = line[len("\tplural: "):]
                    plural = eval(plural) # convert string back to list
                    for item in plural:
                        entry_dict[title]["plural"].add(item)
                elif line.startswith("\t\tflection: ") and title in entry_dict.keys():
                    flection = line[len("\t\tflection: "):]
                    flection = eval(flection) # convert string back to set
                    for item in flection:
                        entry_dict[title]["flection"].add(item)
                elif line.startswith("\t\tsense: ") and title in entry_dict.keys():
                    sense = line[len("\t\tsense: "):]
                    x = sense.split("] ",1)
                    index = x[0][-1]
                    try:
                        sense = x[1]
                        # print(title)
                        # if title == "Kiefer":
                        #     print(genus)
                        if "gender" in entry_dict[title].keys():
                            gender = entry_dict[title]["gender"]
                            if gender == [] or gender == ["0"]: # when there is no gender given
                                if "-" not in entry_dict[title]["senses"].keys(): # when there is a sense given
                                    entry_dict[title]["senses"]["-"] = dict()
                                entry_dict[title]["senses"]["-"][str(index)] = sense
                            else:
                                for item in genus:
                                    entry_dict[title]["senses"][item][str(index)] = sense # sort senses by current gender and index
                        else:
                            if "-" not in entry_dict[title]["senses"].keys():
                                entry_dict[title]["senses"]["-"] = dict()
                            entry_dict[title]["senses"]["-"][str(index)] = sense
                    except IndexError:
                        continue
                elif line.startswith("\t\t\texample(s)") and title in entry_dict.keys():
                    examples = line[len("\t\t\texample(s)"):]
                    examples = eval(examples)
                    if examples != []:
                        for item in examples:
                            x = item.split("] ",1)
                            if len(x) >= 2:
                                sense = x[0][-1]
                                sentence = x[1]
                                sentence = sentence.translate(str.maketrans('', '', string.punctuation)) # remove all punctuation
                                sentence = sentence.translate(str.maketrans("","",'“')) # remove "
                                sentence = sentence.translate(str.maketrans("","",'„'))
                                sentence = sentence.translate(str.maketrans("","","»"))
                                sentence = sentence.translate(str.maketrans("","","«"))
                                sentence = sentence.translate(str.maketrans("","","‘"))
                                sentence = sentence.translate(str.maketrans("","","‚"))
                                if sentence.startswith("Beispiele fehlen"):
                                    continue
                                elif " " in title or "-" in title: # because those can't be kept due to prior preprocessing
                                    continue
                                elif title in sentence.split():
                                    entry_dict[title]["examples"][str(sense)].add(sentence)
                                elif "flection" in entry_dict[title].keys():
                                    for item in entry_dict[title]["flection"]:
                                        if item in sentence:
                                            entry_dict[title]["examples"][str(sense)].add(sentence)
                                            break
                                    if sentence not in entry_dict[title]["examples"][str(sense)]:
                                        ausnahmen.write(title + "\t" + sentence + "\n")
                                else:
                                    ausnahmen.write(title + "\t" + sentence + "\n")
    # print(entry_dict["Kiefer"].items())
    return entry_dict

def find_sets(entry_dict):
    number_pairs = [] # list of singulars and plurals with own sense
    gender_list = []
    others = []
    for title in entry_dict.keys():
        if "plural" in entry_dict[title].keys():
            plural = entry_dict[title]["plural"]
            for item in plural:
                if item == "none": # only use existing plurals
                    continue
                if item in entry_dict.keys() and entry_dict[item] != entry_dict[title]: # when plural has an own entry, which is not the current entry (when plural is written the same as singular)
                    number_pairs.append((title,item)) # add all pairs of singular and plural with own sense to list
        if "gender" in entry_dict[title].keys():
            gender = entry_dict[title]["gender"]
            if len(gender) > 1:
                gender_list.append(title)
        try:
            if title not in gender_list: # if title has no gender-ambiguity
                for item in number_pairs: 
                    if title in item:
                        raise KeyError # when title has number-ambiguity, we don't need it here
                others.append(title)# only continues here when title has no gender- or number-ambiguity
        except KeyError:
            continue
    return (number_pairs,gender_list,others)

# def examples(number_pairs,gender_list):
#     """
#     Find examples from WordNet, and add them to the corpus - TODO
#     """
#     new_examples = dict() # dict for new examples, have to be added to the correct sense
#     for (singular,plural) in number_pairs:
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
    # print(entry_dict["Kiefer"])
    (number_pairs,gender_lists,others) = find_sets(entry_dict)
    # print(gender_lists)
    # print(number_pairs,"\n",gender_lists)
    # new_examples = examples(number_pairs,gender_lists)