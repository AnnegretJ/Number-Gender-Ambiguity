# german_wiktionary

# de_wiktionary.py
This file filters all neccessary information from the German dump for any specified language, and is specifically built to deal with the structure given by German Wiktionary. This file is not supposed to be called directly as a whole, but for individual functions or using other files such as start_wiktionary.py.
## Imports:
* xml.etree.cElementTree
* re
* os
* defaultdict (from collections)
* wordnet (from nltk.corpus)
* sys
* language_check
* string
* tqdm
## Functions:
* write_dict(entries,title,language)
* replace_words_in_examples_new(word,sentence,tool)
* german_xml_parser(language,infile,outfile,entries,plurals,n)
### write_dict(entries,title,language)
Helper function for writing the final output in a dictionary
* param entries: dictionary for entries, containing a dictionary at key 'title' which contains key 'textbit', with value of textpart containing all relevant information of original input-file (type: dict)
* param title: the currently observed word (type: str)
* param language: the language of the current entries (supported for English/German/Spanish) (type: str)
* output: - 
### replace_words_in_examples_new(word,sentence,tool)
instead of deleting entries where word does not appear in an example sentence, replace the appearing synonym with the word
* param word: the currently observed word (type: str)
* param sentence: the currently observed example sentence (type: str)
* param tool: a tool for correcting grammar (type: language_check.LanguageTool)
* output: adjusted example sentence (type: str)
### german_xml_parser(language,infile,outfile,entries=dict(),plurals=set(),n=0)
Parser for German Wiktionary-dumps
* param language: language of input-pages (type: str)
* param infile: directory of file containing Wiktionary-entries in .xml format (type: xml-file)
* param outfile: directory of output-file (type: txt-file)
* param entries: dictionary for collecting information on individual entries (type: dict)
* param plurals: set to contain all possible plurals (type: set)
* param n: counter (type: int)
* output: File containing all relevant data, with structure (type: txt-file)
