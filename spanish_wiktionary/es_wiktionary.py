# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 12:27 2020
Last updated on Nov 22 12:27 2020

@original_author: Annegret
"""

import xml.etree.cElementTree as ET
import re
import os
from collections import defaultdict
from nltk.corpus import wordnet as wn
import sys
# sys.path.insert(1, "..\\english_wiktionary\\")
# from en_wiktionary import english_xml_parser
# sys.path.insert(1, "..\\german_wiktionary\\")
# from de_wiktionary import german_xml_parser
from tqdm import tqdm

def get_plural_wiktionary(textbit):
    plurals = []
    pattern = re.compile("{{forma sustantivo plural|(.*?)}}")
    for line in textbit:
        if pattern.search(line):
            plurals.append(pattern.search(line))
    return plurals
        

def write_file(language,title,f,textbit):
    senses = dict()
    examples = dict()
    all_gender = defaultdict(list)
    f.write("title: " + str(title) + "\n")
    plurals = get_plural_wiktionary(textbit)
    f.write("\tplural: " + str(plurals) + "\n")
    for line in textbit.split("\n"):
        if language == "Spanish" or language == "German":
            if line.startswith("=== {{sustantivo "): # e.g. sustantivo femenino
                if language == "Spanish":
                    gender = line[len("=== {{sustantivo "):-len("|es}} ===")]
                elif language == "German":
                    gender = line[len("== {{sustantivo "):-len("|de}} ===")]
                if "|" in gender:
                    gender = gender[:-len("|es}} p'")]
                if "}" in gender:
                    gender = gender[:-len("}}")]
                if gender == "propio": # when it's a name
                    continue
                all_gender[title].append(gender)
            elif line.startswith(";") and line[1].isdigit():
                senses[line[1]] = line[2:] # senses[index] = sense
                examples[line[1]] = []
        elif language == "English":
            if line.startswith(";") and line[1].isdigit():
                senses[line[1]] = line[2:]
                examples[line[1]] = []
    f.write("\tgender: " + str(all_gender[title]) + "\n")
    # if senses == {}:
    #     n = 1
    #     for item in wn.synsets(title,"n",lang="spa"): # find the according wiktionary noun synsets 
    #         wn_examples = item.examples()
    #         # print(item,wn_examples)
    #         if len(wn_examples) > 0:
    #             senses[n] = item
    #             if n in examples.keys():
    #                 examples[item].append(wn_examples)
    #             else:
    #                 examples[item] = wn_examples
    #             n += 1
    for (index,sense) in senses.items():
        f.write("\t\tsense " + str(index) + ": " + str(sense) + "\n")
        for (sense_,example) in examples.items():
            if sense == sense_:
                f.write("\t\t\texample "+ str(index) + ": " + str(example) + "\n")
    f.write("\n\n")

def spanish_xml_parser(language,infile,outfile,n):
    tree = ET.parse(infile)
    root = tree.getroot()        
    i = 0 # counter for entries
    for child in root:
        for child2 in child:
            if child.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                for grandchild in child2: # the "page" part of the xml file
                    if grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
                        title = grandchild.text # this is the title of the entry -> the word, this happens in the first iteration
                        grandchild.clear()
                    elif grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
                        for element in grandchild.findall("{http://www.mediawiki.org/xml/export-0.10/}text"): # this is the case for every iteration after the first one
                            # we are talking about the text-part containing the languages, not the one containing information on flection
                            text_wiki = element.text
                            if text_wiki: # when there is any text in this part of the tree
                                if "leng=es" in text_wiki or "leng=de" in text_wiki or "leng_en" in text_wiki: # find the spanish-section
                                    for textbit in text_wiki.split('\n\n'):
                                        if "=== {{sustantivo" in textbit: # when it's a noun
                                            write_file(language,title,outfile,textbit)
                                            break
                            else:
                                element.clear()
                    else:
                        grandchild.clear()
                n += 1
        else:
            pass
            child.clear()

