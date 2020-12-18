# Number-Gender-Ambiguity

This project is used to gather data from Wiktionary and WordNet, and use it to calculate word vectors of nouns using BERT, with focus on disambugiation of number- and gender-ambiguity in English, German, and Spanish.
All files have been tested using Python 3 on Windows 10 and Linux.
What follows is a description of the individual files and their functions.

# split_by_entry.py
The purpose of this file is to take the original Wiktionary-dump (tested on enwiktionary-20200501-pages-articles.xml for English, dewiktionary-20200501-pages-articles.xml for German, and eswiktionary-20200501-pages-articles.xml for Spanish) and split it into individual .xml files containing 50,000 entry-pages each.
Further, entries that do not contain any of the three languages are sorted out, whereas entries that contain one of the other languages in focus are saved in separate files.
```
$ python split_by_entry.py <English/German/Spanish> <filename.xml>
```
## Imports:
* xml.etree.ElementTree
* re
* os
* sys
## Functions: 
* None
## File-Input:
* full wiktionary-dump in .xml-format for English, German, Spanish
## File-Output:
* <english/german/spanish>_from_<english/german/spanish>_dump.xml
* <english/german/spanish>_wiktionary/wiktionaries/by_entry/<en/de/es>-wiktionary_short_<1,2,...,n-1,n>.xml

# start_wiktionary.py
This file is used to gather all neccessary information on nouns out of the files produced by split_by_entry.py, and save them in individual files. As the information-structure on each of these .xml-files is different, the python-file needs to access three other files, that are specified later on: en_wiktionary.py, de_wiktionary.py, and es_wiktionary.py.
```
$ python start_wiktionary.py <English/German/Spanish>
```
## Imports:
* sys
* tqdm
* os
## Functions:
* None
## File-Input:
* <english/german/spanish>_from_<english/german/spanish>_dump.xml
* <english/german/spanish>_wiktionary/wiktionaries/by_entry/<en/de/es>-wiktionary_short_<1,2,...,n-1,n>.xml
## File-Output
* <english/german/spanish>_wiktionary/wiktionaries/<en/de/es>-wiktionary.new.txt

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
