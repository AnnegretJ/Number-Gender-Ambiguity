# english_wiktionary

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
Find relevant data in English Wiktionary-page
* param language: Specified language of the file (specified for English/German/Spanish) (type: str)
* param title: title of the currently observed page/the current word (type: str)
* param filename: name/directory of output-file (type: str)
* param cat: text-part containing all necessary information (type: str)
* output: File containing all relevant data, with structure (type: txt-file) 
  
      title: <title>\n
  
      \t plural: [<plural_1>,...,<plural_n>]\n
      
      \t gender: [<gender_1>,...,<gender_n>]\n
      
      \t\t sense1: <sense>\n
      
      \t\t\t example(s)1: [<example_1>,...,<examples_n>]\n
      
      ...
      
      \t\t sensen: <sense>\n
      
      \t\t\t example(s)n: [<example_1>,...,<examples_n>]\n\n
      
      ...
### replace_words_in_examples_new(word,sentence,tool)
instead of deleting entries where word does not appear in an example sentence, replace the appearing synonym with the word
* param word: the word supposed to be found in sentence (type: str)
* param sentence: an example sentence for a sense of word, that does not contain word (type: str)
* param tool: a tool for correcting grammar (type: language_check.LanguageTool)
* output: adjusted example (type: str)
 
 ### english_xml_parser(language,infile,outfile)
 Parser for English Wiktionary-dumps
* param language: language of input-pages (type: str)
* param infile: directory of file containing Wiktionary-entries in .xml format (type: xml-file)
* param outfile: directory of output-file (type: txt-file)
* output: -
