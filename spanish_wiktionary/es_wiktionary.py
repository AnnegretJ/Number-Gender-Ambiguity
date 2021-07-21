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
# from nltk.corpus import wordnet as wn
# import language_check # some module for grammar-checking
import sys
# from tqdm import tqdm

def get_plural_wiktionary(textbit):
    """
    Helper-function to find possible plurals\n
    ;param textbit: textpart of Wiktionary-page containing relevant information\n
    ;returns: list of all possible plurals\n
    """
    plurals = []
    pattern = re.compile("{{forma sustantivo plural|(.*?)}}")
    for line in textbit:
        if pattern.search(line):
            plurals.append(pattern.search(line))
    return plurals
        

def write_file(language,shorts,title,f,textbit):
    """
    Find relevant data in Spanish Wiktionary-page: \n
    plural (list of str)\n
    gender (list of str)\n
    senses (list of str)\n
    example sentences (list of str)\n\n
    ;param language: (str) Specified language of the file (specified for English/German/Spanish)\n
    ;param title: (str) title of the currently observed page/the current word\n
    ;param f: (txt-file) directory of output-file\n
    ;param textbit: textpart of Wiktionary-page containing relevant information\n
    ;returns: File containing all relevant data, with structure\n
    title: <title>\n
    \t plural: [<plural_1>,...,<plural_n>]\n
    \t gender: [<gender_1>,...,<gender_n>]\n
    \t\t sense1: <sense>\n
    \t\t\t example(s)1: [<example_1>,...,<examples_n>]\n
    ...
    \t\t sensen: <sense>\n
    \t\t\t example(s)n: [<example_1>,...,<examples_n>]\n\n
    ...
    """
    senses = dict()
    examples = dict()
    inflections = dict()
    all_gender = defaultdict(list)
    f.write("title: " + str(title) + "\n")
    plurals = get_plural_wiktionary(textbit)
    f.write("\tplural: " + str(plurals) + "\n")
    current = "" # current sense
    next_line_example = False
    for line in textbit.split("\n"):
        if line.startswith("=== {{sustantivo "): # e.g. sustantivo femenino
            if language != "english":
                gender = line[len("=== {{sustantivo "):-len("|" + shorts[language] + "}} ===")]
                if "|" in gender:
                    gender = gender[:-len("|es}} p'")]
                if "}" in gender:
                    gender = gender[:-len("}}")]
                if gender == "propio": # when it's a name
                    continue
                elif len(gender.split()) >= 3: # e.g. "feminino y masculino"
                    every = gender.split()
                    if "{{sustantivo" in every:
                        every.remove("{{sustantivo")
                    if "y" in every:
                        every.remove("y")
                    elif "o" in every:
                        every.remove("o")
                    all_gender[title].extend(every)
                else:
                    all_gender[title].append(gender)
        elif line.startswith("=== Inflexión"): # find inflections
            inflections[title] = set()
        elif line.startswith("| [["):
            form = line.split("[[")[-1].strip("]")
            inflections[title].add(form)
        # find senses
        elif line.startswith(";") and line[1].isdigit():
            examples[line[1]] = []
            current = line[1] # save index of current sense
            sense = line[2:]
            items = sense.split()
            if "|leng=" in items[0]:
                del items[0]
            sense = "".join(items)
            sense.strip("[").strip("]").strip("{").strip("}")
            senses[current] = sense # senses[index] = sense
        # find examples
        elif line.startswith("{{ejemplo}}"):
            examples[current].append([line[len("{{ejemplo}} "):]]) # end of line is example sentence
        elif line.startswith(":*'''Ejemplo:''' ") or line.startswith(":*'''Ejemplo''': "):
            if "'' -" in line:
                parts = line[len(":*'''Ejemplo:'''" ):].split("'' -")
                sentence = parts[0]
            elif "'' =" in line:
                parts = line[len(":*'''Ejemplo:'''" ):].split("'' =")
                sentence = parts[0]
            else:
                sentence = line[len(":*'''Ejemplo:'''" ):]
            examples[current].append(sentence)
        elif line.startswith("{{ejemplo|"):
            reference = line[len("{{ejemplo|"):].strip("}")
            parts = reference.split("|")
            sentence = parts[0]
            examples[current].append(sentence)
        elif line.startswith(":*'''Ejemplo:'''") and line.endswith(":*'''Ejemplo:'''"): # when this is the entire line
            next_line_example = True
        elif line.startswith(":* Ejemplo: "):
            parts = line.split("''")
            sentence = parts[1]
            examples[current].append(sentence)
        if next_line_example:
            # find the example sentence in a quote
            if "'''" in line:
                parts = line.split(", '''")
                closer = parts[-1].split("''', ")
                sentence = closer[0]
            elif "&quot;" in line:
                parts = line.split("&quot;")
                sentence = parts[1]
            else:
                sentence = line[len(":: "):]
            examples[current].append(sentence)
            next_line_example = False
    if title in inflections.keys():
        f.write("\tinflection: " + str(inflections[title]) + "\n")
    f.write("\tgender: " + str(all_gender[title]) + "\n")
    # find additional data from Princeton WordNet for English
    for (index,sense) in senses.items():
        f.write("\t\tsense " + str(index) + ": " + str(sense) + "\n")
        for (sensename,example) in examples.items():
            if index == sensename:
                f.write("\t\t\texample "+ str(index) + ": " + str(example) + "\n")
    f.write("\n\n")

def spanish_xml_parser(language,shorts,infile,outfile):
    """
    Parser for Spanish Wiktionary-dumps\n
    ;param language: (str) language of input-pages\n
    ;param infile: (xml-file) directory of file containing Wiktionary-entries in .xml format\n
    ;param outfile: (txt-file) directory of output-file\n
    ;returns: -
    """
    tree = ET.parse(infile)
    root = tree.getroot()        
    i = 0 # counter for entries
    for child in root:
        for child2 in child:
            # find individual page
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
                                if "leng=" + shorts[language] in text_wiki:
                                    for textbit in text_wiki.split('\n\n'):
                                        if "=== {{sustantivo" in textbit: # when it's a noun
                                            write_file(language,shorts,title,outfile,textbit)
                                            break
                            else:
                                element.clear()
                    else:
                        grandchild.clear()
