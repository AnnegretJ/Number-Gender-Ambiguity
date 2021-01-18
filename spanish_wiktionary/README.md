# spanish_wiktionary
# es_wiktionary.py
This file filters all neccessary information from the Spanish dump for any specified language, and is specifically built to deal with the structure given by Spanish Wiktionary. This file is not supposed to be called directly as a whole, but for individual functions or using other files such as start_wiktionary.py.
## Imports
* xml.etree.cElementTree
* re
* os
* defaultdict (from collections)
* wordnet (from nltk.corpus)
* language_check
* sys
* tqdm

## Functions
* get_plural_wiktionary(textbit)
* write_file(language,title,f,textbit)
* spanish_xml_parser(language,infile,outfile)
* replace_words_in_examples_new(word,sentence,tool)

### get_plural_wiktionary(textbit)
Helper-function to find possible plurals
* param textbit: textpart of Wiktionary-page containing relevant information (type: str)
* output: list of all possible plurals (type: list)

### write_file(language,title,f,textbit)
Find relevant data in Spanish Wiktionary-page
* param language: (str) Specified language of the file (specified for English/German/Spanish) (type: str)
* param title: (str) title of the currently observed page/the current word (type: str)
* param f: (txt-file) directory of output-file (type: txt-file)
* param textbit: textpart of Wiktionary-page containing relevant information (type: str)
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

### spanish_xml_parser(language,infile,outfile)
Parser for Spanish Wiktionary-dumps
* param language: language of input-pages (type: str)
* üaram infile: directory of file containing Wiktionary-entries in .xml format (type: xml-file)
* param outfile: directory of output-file (type: txt-file)
* output: -

### replace_words_in_examples_new(word,sentence,tool)
instead of deleting entries where word does not appear in an example sentence, replace the appearing synonym with the word
* param word: the word supposed to be found in sentence (type: str)
* param sentence: an example sentence for a sense of word, that does not contain word (type: str)
* param tool: a tool for correcting grammar (type: language_check.LanguageTool)
* output: adjusted example (type: str)
