# -*- coding: utf-8 -*-
"""
Last Updated on Mon Sep 17 16:20 2020

@author: Annegret
"""

from collections import defaultdict
# from nltk.corpus import wordnet as wn
import string

def read_files(filename):
    with open(filename,mode="r",encoding="utf-8") as data:
        entry_dict = dict()
        for line in data:
            if line.startswith("title: "):
                title = line[len("title: "):]
                title = title.strip("\n")
                if title not in entry_dict.keys():
                    entry_dict[title] = defaultdict(set)
                    entry_dict[title]["examples"] = defaultdict(set)
                    entry_dict[title]["senses"] = dict()
            elif line.startswith("\tgender: ") and title in entry_dict.keys(): # genus = gender
                genus = line[len("\tgender: "):]
                genus = eval(genus)
                for item in genus:
                    if item not in entry_dict[title]["senses"].keys():
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
            elif line.startswith("\t\tsense") and title in entry_dict.keys():
                index = line[len("\t\tsense"):][0]
                sense = line[len("\t\tsense" + index + ": "):]
                try:
                    if "gender" in entry_dict[title].keys():
                        gender = entry_dict[title]["gender"]
                        if gender == [] or gender == ["0"]: # when there is no gender given
                            if "-" not in entry_dict[title]["senses"].keys(): # when there is a sense given
                                entry_dict[title]["senses"]["-"] = dict()
                            entry_dict[title]["senses"]["-"][str(index)] = sense
                        else:
                            for item in gender:
                                entry_dict[title]["senses"][item][str(index)] = sense # sort senses by current gender and index
                    else:
                        if "-" not in entry_dict[title]["senses"].keys():
                            entry_dict[title]["senses"]["-"] = dict()
                        entry_dict[title]["senses"]["-"][str(index)] = sense
                except IndexError:
                    continue
            elif line.startswith("\t\t\texample(s)") and title in entry_dict.keys():
                index = line[len("\t\t\texample(s)"):][0]
                examples = line[len("\t\t\texample(s)" + index + ": "):]
                examples = eval(examples)
                if examples != []:
                    for item in examples:
                        x = item.split("] ",1)
                        if len(x) >= 2:
                            sense = x[0][-1]
                            sentence = x[1]
                            # punctuation and "" attached to a word can lead to not finding the word in this sentence
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
                                entry_dict[title]["examples"][index].add(sentence)
                            elif "flection" in entry_dict[title].keys():
                                for item in entry_dict[title]["flection"]:
                                    if item in sentence:
                                        entry_dict[title]["examples"][index].add(sentence)
                                        break
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

if __name__ == "__main__":
    path = "wiktionaries\\"
    filename = path + "dewiktionary-new.txt"
    entry_dict = read_files(filename)
    (number_pairs,gender_lists,others) = find_sets(entry_dict)