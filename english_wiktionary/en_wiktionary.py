# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 17:18:54 2020
Last updated on Nov 12 17:31 2020

@original_author: Lenka
@follow_ups: Annegret
"""

import xml.etree.cElementTree as ET
import re
import os
from collections import defaultdict
from nltk.corpus import wordnet as wn
import sys
import language_check # some module for grammar-checking



def get_plural_wiktionary(text_wiki, stem):
    """
    Helper function for getting plural information from wiktionary entry \n
    ;param text_wiki: one entry from Wiktionary data \n
    ;param stem: stem of a word/the word itself\n
    ;return: plural of the entry as list containing all possible plural-forms\n
    """   
    plural = []
    # specify regex for possible plural-forms/positions of plural in text
    re_plural_only = re.compile("{{en-plural noun}}")
    re_plural_none = re.compile("{{en-noun\|\-}}")
    re_plural_none_or_more = re.compile("{{en-noun\|\-\|([A-Za-z|æ' ]+)}}")
    re_plural_s = re.compile("{{en-noun(\|\~\|*(es|s)*)*}}") # kann "~" als ersatz für s anhängen nicht erkennen
    re_plural_s_or_more = re.compile("{{en-noun\|[\~\|]*(s|es)*\|([A-Za-z|æ' ]+)}}")
    re_plural_diff = re.compile("{{en-noun\|([A-Za-z|æ' ]+)?(\|([A-Za-z|æ' ]+)?)*}}")
    re_plural_head = re.compile("{{en-noun|head=\[\[[A-Za-z]+\]\]\[\['s\]\] \[\[[a-z]+]\]\]\|\~}}")
    # find which occurence fits the current page
    if re_plural_s.search(text_wiki): # search the entire text for a plural form, repeat with every variation until result is found
        splitlist = re_plural_s.search(text_wiki).group().split("|")
        if len(splitlist) == 1: # when it only says "en-noun"
            pluralform = stem + "s" # words with plural s
        else: # when there is additional information on the type of ending, e.g. "es" or "~"
            for i in splitlist[-1]:
                if not i.isalpha() and not i == "~":
                    splitlist[-1] = splitlist[-1].strip(i)
            if splitlist[-1] == "~":
                pluralform = stem + "s"
            else:
                pluralform = stem + splitlist[-1]
        plural.append(pluralform)
    elif re_plural_none.search(text_wiki):
        plural.append('none') # words without plural
    elif re_plural_none_or_more.search(text_wiki):
        plural.append('none') # words with either no plural or some plural
        mo = re_plural_none_or_more.search(text_wiki)
        for i in range(1,len(mo.group().split("|"))): # for all possibilities of plurals
            pluralform = mo.group().split("|")[i]
            for i in pluralform:
                    if not i.isalpha():
                        pluralform = pluralform.strip(i)
            if pluralform == "":
                continue
            if len(pluralform) <= 2:
                plural.append(stem + pluralform) # when it's only the ending (nonsense -> nonsenses)                
            else:
                plural.append(pluralform) # when the entire word is written (accessibility -> accessibilites)
    elif re_plural_only.search(text_wiki):
        plural = ["plural only"] # words that only exist as plural form
    # cases for multiple plurals
    elif re_plural_s_or_more.search(text_wiki): # now also containing words formerly dealed with in re_plural_head
        mo = re_plural_s_or_more.search(text_wiki)
        for i in range(1,len(mo.group().split("|"))):
            try:
                pluralform = mo.group().split("|")[i]
                for x in pluralform:
                    if not x.isalpha() and x != "|":
                        pluralform = pluralform.strip(x)
                if len(pluralform) <= 2:
                    plural.append(stem + pluralform)
                else:
                    plural.append(pluralform)
            except IndexError: # for "encyclopedia", it couldn't see that there were two entries instead of one, so additional splitting was necessary
                double = plural.pop() # remove the last item from the list
                doubles = double.split("|") # split it into the two different plurals it contains
                plural.extend(doubles)
    elif re_plural_diff.search(text_wiki):
        mo = re_plural_diff.search(text_wiki) # words with other plural
        for i in range(1,len(mo.group().split("|"))): # for all possibilities of plurals
            try:
                pluralform = mo.group().split("|")[i]
                for x in pluralform:
                        if not x.isalpha() and x != "|":
                            pluralform = pluralform.strip(x)
                if len(pluralform) <= 2:
                    plural.append(stem + pluralform) # when it's only the ending (nonsense -> nonsenses)
                else:
                    plural.append(pluralform) # when the entire word is written (accessibility -> accessibilites)
            except IndexError:
                double = plural.pop()
                doubles = double.split("|")
                plural.extend(doubles)
    elif re_plural_head.search(text_wiki):
        pluralform = stem + "s"
        plural.append(pluralform)
    else:
        plural.append('unspecified')
    return plural


def write_file(language,title,filename,cat):
    """
    Find relevant data in English Wiktionary-page: \n
    plural (list of str)\n
    gender (list of str)\n
    senses (list of str)\n
    example sentences (list of str)\n\n
    ;param language: (str) Specified language of the file (specified for English/German/Spanish)\n
    ;param title: (str) title of the currently observed page/the current word\n
    ;param filename: (str) name/directory of output-file\n
    ;param cat: (str) text-part containing all necessary information\n
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
    if ":" in title: # when it is some kind of help page (not an actual entry)
        return # skip the entire entry
    if "=Noun==" in cat: # get the "noun" category
        senses = dict()
        filename.write("title: " + str(title) + "\n")
        plural= get_plural_wiktionary(cat,title) # get the plural by current category and title
        filename.write("\tplural: " + str(plural) + "\n")
        lines = cat.split("\n")
        current_sense = ""
        all_gender = defaultdict(list)
        for line in lines:
            # find senses
            if line.startswith('# ') and not 'alternative' in line: # when the line contains a meaning that is not "being the alternative of another word"
                sense = line # this line equals the sense/meaning
                current_sense = sense
            # find gender in Spanish data
            elif language == "Spanish" and line.startswith("{{es-noun|"):
                current = line.split("|")
                gender = current[1]
                all_gender[title].append(gender)
            # fiind gender in German data
            elif language == "German" and line.startswith("{{de-noun|"):
                current = line.split("|")
                gender = current[1]
                all_gender[title].append(gender)
            # find example sentences
            elif line.startswith("#* {{"): # when the line is a quote, it usually contains an example sentence for the former line
                if "passage=" in line: # when there is a passage for the example sentence
                    example = line.split("passage=")[1] # find the "passage" part
                    example = example.replace("}}","") # remove the closing brackets at the end of the line
                    if current_sense not in senses.keys():
                        senses[current_sense] = []
                    senses[current_sense].append(example)
                elif "passage-" in line:
                    example = line.split("passage-")[1]
                    example = example.replace("}}","")
                    if current_sense not in senses.keys():
                        senses[current_sense] = []
                    senses[current_sense].append(example)
                elif "passage = " in line:
                    example = line.split("passage = ")[1]
                    example = example.replace("}}","")
                    if current_sense not in senses.keys():
                        senses[current_sense] = []
                    senses[current_sense].append(example)
                else: # not all examples start with "passage"
                    if title in line: # find out if there is an actual example sentence in this line by checking for the current word
                        parts = line.split("|") # the parts of the quote are parted by |
                        for subpart in parts: # for each part of the quote
                            if title in subpart: # find the actual example sentence by searching for the title again
                                example = subpart # the part containing the title is the example sentence
                                if current_sense not in senses.keys():
                                    senses[current_sense] = []
                                senses[current_sense].append(example)
                                break # no need to continue going over the other parts of the quote
            elif line.startswith("#*: ''"):
                example = line.split("#*: ")[1]
                if current_sense not in senses.keys():
                    senses[current_sense] = []
                senses[current_sense].append(example)
    else:
        return # break iteration for the current word when it is not a noun
    filename.write("\tgender: " + str(all_gender[title]) + "\n")
    counter = 1
    all_examples = []
    # get additional senses/examples from WordNet
    if senses == {} and language == "English": # when there are no entries for this word
        for item in wn.synsets(title,"n"): # find the according wiktionary noun synsets 
            examples = item.examples()
            if examples:
                senses[item] = examples
    # fix examples with no occurence of title
    for sense,examples in senses.items():
        filename.write("\t\tsense" + str(counter) + ": " + str(sense) + "\n")
        for example in examples:
            if title in example:
                all_examples.append(example)
            else:
                if language.lower() == "english":
                    tool = language_check.LanguageTool("en-US") # create the tool for grammar-checking the adjusted examples
                elif language.lower() == "german":
                    tool = language_check.LanguageTool("de-DE")
                elif language.lower() == "spanish":
                    tool = language_check.LanguageTool("es")
                new_example = replace_words_in_examples_new(title,example,tool)
                all_examples.append(new_example)
        filename.write("\t\t\texample(s)" + str(counter) + ": " + str(all_examples) + "\n")
        counter += 1
    filename.write("\n\n")     

def replace_words_in_examples_new(word,sentence,tool):
    '''
    instead of deleting entries where word does not appear in an example sentence, replace the appearing synonym with the word\n
    ;param word: (str) the word supposed to be found in sentence\n
    ;param sentence: (str) an example sentence for a sense of word, that does not contain word\n
    ;param tool: (language_check.LanguageTool) a tool for correcting grammar\n
    ;returns: (str) adjusted example\n
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

def english_xml_parser(language,infile,outfile):
    """
    Parser for English Wiktionary-dumps\n
    ;param language: (str) language of input-pages\n
    ;param infile: (xml-file) directory of file containing Wiktionary-entries in .xml format\n
    ;param outfile: (txt-file) directory of output-file\n
    ;returns: -
    """
    tree = ET.parse(infile)
    root = tree.getroot()   
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
                                    for textbit in text_wiki.split('----'):      
                                        if "==" + language + "==" in textbit: # find the section for the current language (English Spanish German)
                                            if "===Etymology" not in textbit: # when there is no etymology
                                                for cat in textbit.split("\n=="): # find the different categories in this subtree
                                                    if title != None:
                                                        write_file(language,title,outfile,cat)
                                            else:
                                                segments = textbit.split('===Etymology') # find etymology
                                                for segment in segments: # for each part of the etymology
                                                    if segment.startswith("===\n"): # find the categories
                                                        for cat in segment.split("\n=="): # for each category
                                                            if title != None:
                                                                write_file(language,title,outfile,cat)
                                                    elif re.match("\s*\d+===",segment): # find other kinds of categories
                                                        for cat in segment.split("\n=="): # for each category
                                                            if title != None:
                                                                write_file(language,title,outfile,cat)
                                else:
                                    element.clear()
                    else:
                        grandchild.clear()
        else:
            pass
            child.clear()
