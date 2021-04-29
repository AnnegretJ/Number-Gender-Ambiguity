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
In this file, the formerly gathered data is processed, so that entries without example sentences are removed and all punctuation is removed from the sentences. All data is sorted into three categories: words containing gender-ambiguity, words containing number-ambiguity, and words containing neither type of ambiguity. Especially large input files are split into smaller files and processed individually, while trying to minimize information loss. This file is called by Use_BERT.py, and is not supposed to be called directly, as it does not create any file output.
```
$ python preprocessing.py
```
## Imports
* defaultdict (from collections)
* wordnet (from nltk.corpus)
* string
* sys
* tqdm
* fsplit.filesplit
* os
* os.path

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
Using the individual categories of data created by preprocessing.py, this file runs each example sentence for each word through BERT, thereby computing word embedding vectors for each word entry based on the given example sentences. Language and model-type can be specified.
```
$ python Use_BERT.py <english/german/spanish> <specific/multilingual>
```
## Imports:
* torch
* pandas
* preprocessing (see above)
* sys
* tqdm
* numpy
* os.path
* transformers

## Functions:
* get_marked_text_from_examples(sentence)
* run_BERT(word,tokenizer,text,model)
* process_number(relevant_pairs,entry_dict,model,tokenizer,frame)
* process_gender(gender_list,entry_dict,model,tokenizer,frame)
* process_other(other,entry_dict,model,tokenizer,frame)
* write_files(language,path,filename,tokenizer,model)
* call_functions(relevant_pairs,other,gender_list,entry_dict,model,tokenizer)

## File-Input:
* <english/german/spanish>_wiktionary/wiktionaries/<en/de/es>_wiktionary-new.txt

## File-Output:
* <english/german/spanish>_wiktionary/<number/gender/other>.csv

### get_marked_text_from_examples(sentence)
get example sentences with special tokens for beginning and end of sentences
* param sentence: (str) sentence that needs to be marked
* returns: marked sentence

### run_BERT(word,tokenizer,text,model)
compute word- and sentence-embeddings for a given word and sentence
* param word: (str) the word to calculate embeddings for
* param tokenizer: BertTokenizer
* param text: (str) example sentence used for context
* param model: specified BERT-model
* returns: tuple (word-embedding,sentence-embedding)

### process_number(relevant_pairs,entry_dict,model,tokenizer,frame)
Process data on number-ambiguity-data and run through BERT
* param relevant_pairs: (list) list containing tuples of sg-pl-pairs
* param entry_dict: (dict) dictionary containing all relevant information
* param model: specified BERT-model
* param tokenizer: BertTokenizer
* param frame: pandas dataframe for file-output
* returns: pandas dataframe containing all calculated vectors

### process_gender(gender_list,entry_dict,model,tokenizer,frame)
Process data on gender-ambiguity-data and run through BERT
* param gender_list: (list) list containing words that have more than one grammatical gender
* param entry_dict: (dict) dictionary containing all relevant information
* param model: specified BERT-model
* param tokenizer: BertTokenizer
* param frame: pandas dataframe for file-output
* returns: pandas dataframe containing all calculated vectors

### process_other(other,entry_dict,model,tokenizer,frame)
Process data on non-ambiguity-data and run through BERT
* param other: (list) list containing all words without number- or gender-ambiguity
* param entry_dict: (dict) dictionary containing all relevant information
* param model: specified BERT-model
* param tokenizer: BertTokenizer
* param frame: pandas dataframe for file-output
* returns: pandas dataframe containing all calculated vectors

### write_files(language,path,filename,tokenizer,model)
write dataframes to files
* param language: specified language (supports English,German,Spanish)
* param path: path for output-file
* param filename: name of input-file
* param tokenizer: BertTokenizer
* param model: specified BERT-model
* returns: files containing pandas dataframes for each type of data in .csv and .pkl format

### call_functions(relevant_pairs,other,gender_list,entry_dict,model,tokenizer)
calls other functions in this file in correct order
* param relevant_pairs: (list) list containing tuples of sg-pl-pairs
* param other: (list) list containing all words without number- or gender-ambiguity
* param gender_list: (list) list containing words that have more than one grammatical gender
* param entry_dict: (dict) dictionary containing all relevant information
* param model: specifiec BERT-model
* param tokenizer: BertTokenizer
* returns: tuple containing pandas dataframes for number ambiguity, no ambiguity (and gender ambiguity if available)

# distances.py
Computes cosine distance, euclidean distance, and manhattan distance for given embedding vectors and saves results in files. First additional argument specifies the type of data ([-n]umber, [-g]ender, [-n]umber and [g]ender, [-o]ther, [-g]ender and [o]ther, [-n]umber and [other], [-a]ll). The second argument specifies language, the third one the type of model with which the embedding vectors have been created in Use_BERT.py

```
$ python graphs.py <-n/-g/-ng/-o/-go/-no/-a> <english/german/spanish> <specific/multilingual>
```

## Imports:
* pandas
* torch
* sys
* numpy
* os
* itertools
* scipy.spatial

## Functions:
* distances(model,path,mode)
* get_distances(first,second,first_vector,second_vector,cos,euc,man)
* read_files(file_1,file_2=None,file_3=None)
* start(data,wordlist,path,mode)

## File-Input:
* <english/german/spanish>_wiktionary/<specific/multilingual>/<number/gender/other>.csv

## File-Output:
* <english/german/spanish>_wiktionary/<specific/multilingual>/<number/gender/number_gender/other/number_other/gender_other/all>_cosine_distances.txt
* <english/german/spanish>_wiktionary/<specific/multilingual>/<number/gender/number_gender/other/number_other/gender_other/all>_euclidean_distances.txt
* <english/german/spanish>_wiktionary/<specific/multilingual>/<number/gender/number_gender/other/number_other/gender_other/all>_manhattan_distances.txt

### distances(model,path,mode)
Used to compute distances between given embedding vectors.
* param model: (dict) dictionary containing information on specific words and their embedding vectors for all available meanings
* param oath: (str) output path
* param mode: (str) type of data (e.g. "number")
* returns: file-output

### get_distances(first,second,first_vector,second_vector,cos,euc,man)
Compute all three distances between two individual vectors and write the results to a file
* param first: word(-sense) of the first vector
* param second: word(-sense) of the second vector
* param first_vector: embedding vector for first
* param second_vector: embedding vector for second
* param cos: file for writing cosine distances
* param euc: file for writing euclidean distances
* param man: file for writing manhattan distances
* returns: -

### read_files(file_1,file_2=None,file_3=None)
Reads in .csv-files created by Use_BERT.py, merges files if more than one is given.
* param file_1: first data file
* param file_2: if given, a second data file of same kind as file_1
* param file_3: if given, a third data file of same kind as file_3
* returns: pandas dataframe from files

### start(data,wordlist,path,mode)
Finds necessary data in dataframe and calls functions in correct order.
* param data: pandas dataframe given from function read_files()
* param wordlist: list of words of which the embedding vectors should be compared
* param path: output path
* param mode: type of data (e.g. "number)
* returns: -
