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
    if language == "german":
        senses = entries[title]["textbit"].split('== {{Wortart|Substantiv|Deutsch}}')
    elif language == "spanish":
        senses = entries[title]["textbit"].split("== {{Wortart|Substantiv|Spanisch}}")
    elif language == "english":
        senses = entries[title]["textbit"].split("== {{Wortart|Substantiv|Englisch}}")
    overview = {"german":"Deutsch Substantiv Übersicht","english":"English Substantiv Übersicht","spanish":"Spanisch Substantiv Übersicht"}
    for sense in senses:
        entries[title][i] = defaultdict(list)
        # find information for German
        entries[title][i]["flection"] = set()
        fields = sense.split("\n{{")
        for field in fields:
            if overview[language] in field:
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
                                if c != "-" and c != "":
                                    entries[title][i]["flection"].add(c)
                            else:
                                c = line.split(" ")[-1]
                                if c != "-" and c != "":
                                    entries[title][i]["flection"].add(c)  
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
                    if any([item in meaning for item in ["Name","Vorname","Nachname","Familienname"]]):
                        continue
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
                    if "<ref>" in e:
                        e = e.split("<ref>")[0]
                    if "/" in e:
                        items = e.split("/")
                        for it in items:
                            if title in it and not it[len(" ''"+title+"'' "):].startswith("<"):
                                e = it
                                break
                    entries[title][i]["examples"][number].append(e)
        i += 1

def german_xml_parser(language,shorts,infile,outfile):
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
    plurals = set()
    entries = dict()
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
                                        if language == "german" and "Substantiv|Deutsch" in textbit: # find the German-section for nouns  
                                            entries[word] = {}
                                            entries[word]["textbit"] = textbit
                                        elif language == "spanish" and "Substantiv|Spanisch" in textbit:
                                            entries[word] = {}
                                            entries[word]["textbit"] = textbit
                                        elif language == "english" and "Substantiv|Englisch" in textbit:
                                            entries[word] = {}
                                            entries[word]["textbit"] = textbit
    for title in entries:
        if "textbit" in entries[title].keys():
            write_dict(entries,title,language)
            del entries[title]["textbit"]
    # find words that look like a plural of another word, but are not actually
    if language == "german":
        word = plurals.pop()
        for item in entries: # title
            if word[:-1] == item or word[:-2] == item: # if the word looks like a pluralversion of the title
                for subitem in entries[item]: # i
                    if word not in entries[item][subitem]["plural"]: # when the word is not already noted as a possible plural
                        entries[item][subitem]["plural"].append(word)
    # write the file
    for el in entries:
        outfile.write("title: " + str(el) + "\n")
        for el2 in entries[el]:
            if "flection" in entries[el][el2] and entries[el][el2]["flection"] != set():
                outfile.write("\tinflection: " + str(entries[el][el2]["flection"]) + "\n")
            if "gender" in entries[el][el2]:
                outfile.write("\tgender: " + str(entries[el][el2]["gender"]) + "\n")
            if "plural" in entries[el][el2]:
                outfile.write("\tplural: " + str(entries[el][el2]["plural"]) + "\n")
            if "senses" in entries[el][el2]:
                for number in entries[el][el2]["senses"]:
                    outfile.write("\t\tsense" +  str(number) + ": " + str(entries[el][el2]["senses"][number]) + "\n")
                    if "examples" in entries[el][el2] and number in entries[el][el2]["examples"]:
                        outfile.write("\t\t\texample(s)" + str(number) + ": " +  str(entries[el][el2]["examples"][number]) + "\n")
        outfile.write("\n")