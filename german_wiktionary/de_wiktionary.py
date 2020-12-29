import os

"""
Last Updated on Nov 12 17:31 2020

@author: Annegret
"""

import xml.etree.cElementTree as ET
import re
from collections import defaultdict
import string
from tqdm import tqdm
import sys
from nltk.corpus import wordnet as wn
import language_check # some module for grammar-checking


def write_dict(entries,title,language):
    """
    Helper function for writing the final output in a dictionary \n
    ;param entries: (dict) dictionary for entries, containing a dictionary at key 'title' which contains key 'textbit', with value of textpart containing all relevant information of original input-file\n
    ;param title: the currently observed word \n
    ;param language: the language of the current entries (supported for English/German/Spanish)\n
    returns: -
    """
    re_number_of = re.compile(":\[(\d+)\]")
    i = 1
    if language == "German":
        senses = entries[title]["textbit"].split('== {{Wortart|Substantiv|Deutsch}}')
    elif language == "Spanish":
        senses = entries[title]["textbit"].split("== {{Wortart|Substantiv|Spanisch}}")
    elif language == "English":
        senses = entries[title]["textbit"].split("== {{Wortart|Substantiv|Englisch}}")
    for sense in senses:
        entries[title][i] = defaultdict(list)
        # find information for German
        if language == "German":
            entries[title][i]["flection"] = set()
        fields = sense.split("\n{{")
        for field in fields:
            # get information for German
            if language == "German" and "Deutsch Substantiv Übersicht" in field:
                morphs = field.split("\n")
                for morph in morphs:
                    if "Genus" in morph:
                        if "=" in morph:
                            g = morph.split("=")[-1]
                        else:
                            g = morph.split(" ",1)[-1]
                        entries[title][i]["gender"].append(g)
                    if "Singular" in morph or "Plural" in morph: # find grammatic inflection
                        lines = morph.split("\n")
                        for line in lines:
                            if "=" in line:
                                c = line.split("=")[-1]
                                entries[title][i]["flection"].add(c)
                            else:
                                c = line.split(" ")[-1]
                                entries[title][i]["flection"].add(c)  
            # get information for Spanish
            elif language == "Spanish" and "Spanisch Substantiv Übersicht" in field:
                morphs = field.split("\n")
                for morph in morphs:
                    if "Genus" in morph:
                        if "=" in morph:
                            g = morph.split("=")[-1]
                        else:
                            g = morph.split(" ",1)[-1]
                        entries[title][i]["gender"].append(g)
                    elif "Plural" in morph or "Pl." in morph:
                        if "=" in morph:
                            plural = morph.split("=")[-1]
                        else:
                            plural = morph.split(" ",1)[-1]
                        entries[title][i]["plural"].append(plural)
            # get information for English
            elif language == "English" and "Englisch Substantiv Übersicht" in field:
                morphs = field.split("\n")
                for morph in morphs:
                    if "Plural" in morph or "Pl." in morph:
                        if "=" in morph:
                            plural = morph.split("=")[-1]
                        else:
                            plural = morph.split(" ",1)[-1]
                        entries[title][i]["plural"].append(plural)
            # find additional plural-versions
            elif "Worttrennung}}" in field:
                infos = field.split("\n")
                for info in infos:
                    if "Pl." in info or "Plural" in info:
                        parts = info.split(",")
                        for part in parts:
                            if "kPl." in part:
                                continue
                            elif "Pl." in part:
                                p = part.split()[-1]
                                p = p.replace("·","")
                                entries[title][i]["plural"].append(p)
            # find senses
            elif "Bedeutungen}}" in field:
                entries[title][i]["senses"] = {}
                field = re.sub("Bedeutungen}}\n","",field)
                meanings = field.split("\n")
                for meaning in meanings:
                    if re_number_of.search(meaning):
                        number_of = re_number_of.search(meaning)
                        number = number_of.group(1)
                        entries[title][i]["senses"][number] = meaning
            # find examples
            elif "Beispiele}}" in field:
                entries[title][i]["examples"] = defaultdict(list)
                field = re.sub("Beispiele}}\n","",field)
                examples = field.split("\n")
                n = 0
                while n < len(examples):
                    if len(examples[n].split()) <= 2:
                        n += 1
                        continue
                    elif examples[n].startswith("="): # when the next category starts
                        break
                    number = examples[n][2]
                    e = examples[n][4:]
                    n += 1
                    if "Beispiele fehlen" in e:
                        continue
                    entries[title][i]["examples"][number].append(e)
        i += 1

def german_xml_parser(language,infile,outfile,entries=dict(),plurals=set(),n=0):
    """
    Parser for German Wiktionary-dumps\n
    ;param language: (str) language of input-pages\n
    ;param infile: (xml-file) directory of file containing Wiktionary-entries in .xml format\n
    ;param outfile: (txt-file) directory of output-file\n
    ;param entries: (dict) dictionary for collecting information on individual entries\n
    ;param plurals: (set) set to contain all possible plurals\n
    ;param n: (int) counter\n
    ;returns: File containing all relevant data, with structure\n
    title: <title>\n
    \t plural: [<plural_1>,...,<plural_n>]\n
    \t gender: [<gender_1>,...,<gender_n>]\n
    \t\t inflection: [<inflection_1>,...,<inflection_n>]\n
    \t\t sense1: <sense>\n
    \t\t\t example(s)1: [<example_1>,...,<examples_n>]\n
    ...
    \t\t sensen: <sense>\n
    \t\t\t example(s)n: [<example_1>,...,<examples_n>]\n\n
    ...
    """
    tree = ET.parse(infile)
    root = tree.getroot()
    for child in root:
        for child2 in child:
            # find page
            if child2.tag == "{http://www.mediawiki.org/xml/export-0.10/}page":
                for child3 in child2:
                    # find word/title
                    if child3.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
                        if child3.text != None:
                            word = child3.text # this is the title of the entry -> the word, this happens in the first iteration
                            if language == "German" and word[-1] == "s" or word[-1] == "n" or word[-2:] == "en" or word[-1] == "e" or word[-2:] == "er": # when the word contains a typical ending for regular plural
                                plurals.add(word) # add word into set of all words that could be a regular plural of some other word
                                # this will be iterated over later on to see which words need to be added to the dictionary
                    elif child3.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
                        for child4 in child3:
                            if child4.tag == "{http://www.mediawiki.org/xml/export-0.10/}text":
                                text_wiki = child4.text
                                if text_wiki:
                                    # add textbit to dictionary
                                    for textbit in text_wiki.split("---"):
                                        if language == "German" and "Substantiv|Deutsch" in textbit: # find the German-section for nouns  
                                            entries[word] = {}
                                            entries[word]["textbit"] = textbit
                                        elif language == "Spanish" and "Substantiv|Spanisch" in textbit:
                                            entries[word] = {}
                                            entries[word]["textbit"] = textbit
                                        elif language == "English" and "Substantiv|Englisch" in textbit:
                                            entries[word] = {}
                                            entries[word]["textbit"] = textbit
    for title in entries:
        if "textbit" in entries[title].keys():
            write_dict(entries,title,language)
            del entries[title]["textbit"]
            # find additional information from WordNet for English data
            if language == "English" and all(entries[title][index]["senses"] == {} for index in entries[title].keys()):
                index = 1
                example_index = 1
                for item in wn.synsets(title,"n"): # find the according WordNet noun synsets 
                    examples = item.examples()
                    actual_examples = []
                    for example in examples:
                        if title in example:
                            actual_examples.append(example)
                        else:
                            tool = language_check.LanguageTool("en-US") # create the tool for grammar-checking the adjusted examples
                            new_example = replace_words_in_examples_new(title,example,tool)
                            actual_examples.append(new_example)
                    entries[title][index]["senses"] = item
                    entries[title][index]["examples"][example_index] = actual_examples
                    index += 1
                    example_index += 1
    # find words that look like a plural of another word, but are not actually
    if language == "German":
        word = plurals.pop()
        for item in entries: # title
            if word[:-1] == item or word[:-2] == item: # if the word looks like a pluralversion of the title
                for subitem in entries[item]: # i
                    if word not in entries[item][subitem]["plural"]: # when the word is not already noted as a possible plural
                        entries[item][subitem]["plural"].append(word)
    # write the file
    for el in entries:
        n += 1
        outfile.write("title: " + str(el) + "\n")
        for el2 in entries[el]:
            if "gender" in entries[el][el2]:
                outfile.write("\tgender: " + str(entries[el][el2]["gender"]) + "\n")
            if "plural" in entries[el][el2]:
                outfile.write("\tplural: " + str(entries[el][el2]["plural"]) + "\n")
            if "flection" in entries[el][el2]:
                outfile.write("\t\tinflection: " + str(entries[el][el2]["flection"]) + "\n")
            if "senses" in entries[el][el2]:
                for number in entries[el][el2]["senses"]:
                    outfile.write("\t\tsense" +  str(number) + ": " + str(entries[el][el2]["senses"][number]) + "\n")
                    if "examples" in entries[el][el2] and number in entries[el][el2]["examples"]:
                        outfile.write("\t\t\texample(s)" + str(number) + ": " +  str(entries[el][el2]["examples"][number]) + "\n")
        outfile.write("\n")

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