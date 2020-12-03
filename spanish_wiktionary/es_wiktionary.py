# language: == {{lengua|es}} == in text
# noun/gender: === Forma sustantiva femenina === in text
# plural: ;1: {{forma sustantivo plural|eme}}. in text

# === Forma sustantiva femenina ===
# ;1: {{forma sustantivo|leng=pl|caso=instrumental|n&#250;mero=singular|nerka}}.
# with sense: ;1 {{mam&#237;feros}}: (''Manis'') {{plm|mam&#237;fero}} [[folidoto]] [[insect&#237;voro]] de cuerpo cubierto por grandes [[escama]]s casi en su totalidad, oriundo de las zonas tropicales de Asia y de &#193;frica.
# examples????

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
sys.path.insert(1, "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\")
from en_wiktionary import *
sys.path.insert(1, "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\german_wiktionary\\")
from de_wiktionary import *

def get_plural_wiktionary(textbit):
    plurals = []
    pattern = re.compile("{{forma sustantivo plural|(.*?)}}")
    for line in textbit:
        if pattern.search(line):
            plurals.append(pattern.search(line))
    return plurals
        

def write_file(title,f,textbit):
    senses = dict()
    examples = dict()
    f.write("title: " + str(title) + "\n")
    plurals = get_plural_wiktionary(textbit)
    f.write("\tplural: " + str(plurals) + "\n")
    for line in textbit.split("\n"):
        if line.startswith("=== {{sustantivo "): # sustantivo femenino
            gender = line[len("=== {{sustantivo "):-len("|es}} ===")]
            f.write("\tgender: " + str(gender) + "\n")
        elif line.startswith(";") and line[1].isdigit():
            senses[line[1]] = line[2:] # senses[index] = sense
            examples[line[1]] = []
    if senses == {}:
        n = 1
        for item in wn.synsets(title,"n",lang="spa"): # find the according wiktionary noun synsets 
            wn_examples = item.examples()
            # print(item,wn_examples)
            if len(wn_examples) > 0:
                senses[n] = item
                if n in examples.keys():
                    examples[item].append(wn_examples)
                else:
                    examples[item] = wn_examples
                n += 1
    for (index,sense) in senses.items():
        f.write("\t\tsense " + str(index) + ": " + str(sense) + "\n")
        for (sense_,example) in examples.items():
            if sense == sense_:
                f.write("\t\t\texample "+ str(index) + ": " + str(example) + "\n")
    f.write("\n\n")

def spanish_from_english(infile,outfile,n):
    english_xml_parser("Spanish",infile,outfile,n=n)

def spanish_from_german(infile,outfile,n):
    entries = dict()
    german_xml_parser("Spanish",infile,outfile,entries,n=n)


# path to data
path = "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\spanish_wiktionary\\wiktionaries\\"
with open(path +'eswiktionary-new.txt', mode='w+', encoding="utf8") as wiktionary_out:
    n = 0
    for filename in os.listdir(path + "by_entry\\"): # \ for Windows, / for Linux
        continue
        with open(path + "by_entry\\" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
            tree = ET.parse(file_in_wiktionary)
            root = tree.getroot()        
            i = 0 # counter for entries
            for child in root:
                for child2 in child:
                    if child.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                        if (n % 10000 == 0):
                            print(n) # sanity check
                        for grandchild in child2: # the "page" part of the xml file
                            if grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
                                title = grandchild.text # this is the title of the entry -> the word, this happens in the first iteration
                                grandchild.clear()
                            elif grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
                                for element in grandchild.findall("{http://www.mediawiki.org/xml/export-0.10/}text"): # this is the case for every iteration after the first one
                                    # we are talking about the text-part containing the languages, not the one containing information on flection
                                    text_wiki = element.text
                                    if text_wiki: # when there is any text in this part of the tree
                                        if "leng=es" in text_wiki: # find the spanish-section
                                            for textbit in text_wiki.split('\n\n'):
                                                if "=== {{sustantivo" in textbit: # when it's a noun
                                                    write_file(title,wiktionary_out,textbit)
                                                    break
                                    else:
                                        element.clear()
                            else:
                                grandchild.clear()
                        n += 1
                else:
                    pass
                    child.clear()
    path = "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\"
    with open(path + "spanish_from_english_dump.xml",encoding="utf-8") as e:
        spanish_from_english(e,wiktionary_out,n)
    with open(path + "spanish_from_german_dump.xml",encoding="utf-8") as g:
        spanish_from_german(g,wiktionary_out,n)

