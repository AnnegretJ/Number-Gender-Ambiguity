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

# preprocessing.py
In this file, the formerly gathered data is processed, so that entries without example sentences are removed and all punctuation is removed from the sentences. All data is sorted into three categories: words containing gender-ambiguity, words containing number-ambiguity, and words containing neither type of ambiguity. This file is called by Use_BERT.py, and is not supposed to be called directly, as it does not create any file output.
```
$ python preprocessing.py
```
## Imports
* defaultdict (from collections)
* wordnet (from nltk.corpus)
* string
* sys
* tqdm

## Functions
* read_files(filename)
* find_sets(entry_dict)

### read_files(filename)
Function to read in files containing necessary information
* param filename: directory of input-file (type: txt-file)
* output: dictionary containing all informations of the file (type: dict)

### find_sets(entry_dict)
Find relevant data on number- or gender-ambiguity
* param entry_dict: dictionary containing all relevant information (type: dict)
* output: (list of word-pairs (sg,pl) with number-ambiguity, list of words with gender-ambiguity, list of words with none of those ambiguity-types) (type: tuple)

# Use_BERT.py
Using the individual categories of data created by preprocessing.py, this file runs each example sentence for each word through BERT
TODO
