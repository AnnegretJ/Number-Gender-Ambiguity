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
import language_check # some module for grammar-checking
import sys
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
    current = "" # current sense
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
                current = line[1] # save index of current sense
            elif line.startswith("{{ejemplo}}"):
                examples[current].append([line[len("{{ejemplo}} "):]]) # end of line is example sentence
            elif line.startswith(":*'''Ejemplo''': "):
                examples[current].append([line[len(":*'''Ejemplo''': "):]])
    f.write("\tgender: " + str(all_gender[title]) + "\n")
    if language == "English" and senses == {}:
        index = 0
        for item in wn.synsets(title,"n"): # find the according wiktionary noun synsets 
            senses[index] = item
            sentences = item.examples()
            actual_examples = []
            for example in sentences:
                if title in example:
                    actual_examples.append(example)
                else:
                    tool = language_check.LanguageTool("en-US") # create the tool for grammar-checking the adjusted examples
                    new_example = replace_words_in_examples_new(title,example,tool)
                    actual_examples.append(new_example)
            examples[index] = actual_examples
            index += 1
    for (index,sense) in senses.items():
        f.write("\t\tsense " + str(index) + ": " + str(sense) + "\n")
        for (sensename,example) in examples.items():
            if sense == sensename:
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
                                if "leng=es" in text_wiki or "leng=de" in text_wiki or "leng=en" in text_wiki: # find the spanish-section
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

def replace_words_in_examples_new(word,sentence,tool):
    '''
    instead of deleting entries where word does not appear in an example sentence, we replace the appearing synonym with the word
    returns adjusted examples
    '''
    replace_item = ""
    synonyms = wn.synsets(word, "n") # find all synonyms of the word, that are nouns as well
    for syn in synonyms:
        syn_lemmas = syn.lemma_names() # find the lemma for the synonym
        for s in syn_lemmas:
            if s in sentence.split(): # check if the synonym appears in the example sentence
                replace_item = re.sub(r"\b{}\b".format(s),word,sentence.lower()) # replace the word by its synonym => this might lead to grammar problems
                matches = tool.check(replace_item) # check if the sentence is grammatically correct
                n = 0
                while n < len(matches):
                    new = language_check.correct(replace_item, matches[n:]) # correct the grammar by using the possible solutions in matches
                    if word not in new.split():
                        n += 1
                    else:
                        replace_item = new
                        break
                if word not in replace_item.split():
                    replace_item = ""
    return replace_item 

