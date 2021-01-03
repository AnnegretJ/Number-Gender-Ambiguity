#english_wiktionary

# en_wiktionary.py
This file filters all neccessary information from the English dump for any specified language, and is specifically built to deal with the structure given by English Wiktionary. This file is not supposed to be called directly as a whole, but for individual functions or using other files such as start_wiktionary.py.
## Imports:
* xml.etree.cElementTree
* re
* os
* defaultdict (from collections)
* wordnet (from nltk.corpus)
* sys
* language_check
## Functions:
* get_plural_wiktionary(text_wiki,stem)
* write_file(language,title,filename,cat)
* replace_words_in_examples_new(word,sentence,tool)
* english_xml_parser(language,infile,outfile)
### get_plural_wiktionary(text_wiki,stem)
This function is used to quickly find the plural specified for a word in it's Wikionary-entry.
* param text_wiki: one part of text found under the <text>-tag in the input-file given to write_file(language,title,filename,cat) (type:str)
* param stem: the stem of the observed word/the observed word itself (type:str)
* output: list of possible plurals (type:list)
### write_file(language,title,filename,cat)
TODO
