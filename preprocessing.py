from collections import defaultdict
from nltk.corpus import wordnet as wn
import string
import sys
from tqdm import tqdm

def read_files(filename):
    """
    function to read in files containing necessary information\n
    ;param filename: (txt-file) directory of input-file\n
    ;returns: dictionary containing all informations of the file\n
    """
    with open(filename,mode="r",encoding="utf-8") as data:
        entry_dict = dict()
        # options on how gender is written
        m_genus = ["m","masculine","maskulin","masculino","m}}"]
        f_genus = ["f","feminine","feminin","femenino","f}}"]
        n_genus = ["n","neuter","neutrum","neutro","n}}"]
        for line in tqdm(data):
            # get title
            if line.startswith("title: "):
                title = line[len("title: "):]
                title = title.strip("\n")
                if " " in title or "-" in title: # can't be kept due to removal of punctuation and splitting of sentences later on
                    continue
                if title not in entry_dict.keys():
                    entry_dict[title] = defaultdict(set)
                    entry_dict[title]["examples"] = defaultdict(set)
                    entry_dict[title]["senses"] = dict()
            # get gender
            elif line.startswith("\tgender: ") and title in entry_dict.keys(): # German and Spanish only
                genus = line[len("\tgender: "):]
                genus = eval(genus)
                # make sure all data uses the same string for genus (to avoid doubled entries)
                for item in genus:
                    item.strip("|")
                    item.strip("{")
                    item.strip("}")
                    item.strip("de")
                    item.strip("en")
                    item.strip("es")
                    if item in m_genus:
                        item = "m"
                    elif item in f_genus:
                        item = "f"
                    elif item in n_genus:
                        item = "n"
                    if item not in entry_dict[title]["senses"].keys():
                        entry_dict[title]["senses"][item] = dict()
                    entry_dict[title]["gender"].add(item)
            # get plural
            elif line.startswith("\tplural: ") and title in entry_dict.keys():
                plural = line[len("\tplural: "):]
                plural = eval(plural) # convert string back to list
                for item in plural:
                    entry_dict[title]["plural"].add(item)
            # get inflection
            elif line.startswith("\tflection: ") and title in entry_dict.keys(): # currently only German
                flection = line[len("\tflection: "):]
                flection = eval(flection) # convert string back to set
                for item in flection:
                    entry_dict[title]["flection"].add(item)
            # get senses
            elif line.startswith("\t\tsense") and title in entry_dict.keys():
                index = line[len("\t\tsense"):][0]
                sense = line[len("\t\tsense" + index + ": "):]
                all_gender = entry_dict[title]["gender"]
                if all_gender == set() or all_gender == set("0"): # when there is no gender given
                    if "-" not in entry_dict[title]["senses"].keys(): # when there is a sense given
                        entry_dict[title]["senses"]["-"] = dict()
                    entry_dict[title]["senses"]["-"][str(index)] = sense
                else:
                    for item in all_gender:
                        entry_dict[title]["senses"][item][str(index)] = sense # sort senses by current gender and index
            # get examples
            elif line.startswith("\t\t\texample(s)") and title in entry_dict.keys():
                index = line[len("\t\t\texample(s)"):][0]
                examples = line[len("\t\t\texample(s)" + index + ": "):]
                examples = eval(examples)
                if examples != []:
                    for sentence in examples:
                        # punctuation and "" attached to a word can lead to not finding the word in this sentence
                        sentence = sentence.translate(str.maketrans('', '', string.punctuation)) # remove all punctuation
                        sentence = sentence.translate(str.maketrans("","",'“')) # remove "
                        sentence = sentence.translate(str.maketrans("","",'„'))
                        sentence = sentence.translate(str.maketrans("","","»"))
                        sentence = sentence.translate(str.maketrans("","","«"))
                        sentence = sentence.translate(str.maketrans("","","‘"))
                        sentence = sentence.translate(str.maketrans("","","‚"))
                        if sentence.startswith("Beispiele fehlen"):
                            continue
                        elif title in sentence.split():
                            entry_dict[title]["examples"][index].add(sentence)
                        elif "flection" in entry_dict[title].keys():
                            for item in entry_dict[title]["flection"]:
                                if item in sentence:
                                    entry_dict[title]["examples"][index].add(sentence)
                                    break
    return entry_dict

def find_sets(entry_dict):
    """
    Find relevant data on number- or gender-ambiguity\n
    ;param entry_dict: (dict) dictionary containing all relevant information\n
    ;returns: tuple: (list of word-pairs (sg,pl) with number-ambiguity, list of words with gender-ambiguity, list of words with none of those ambiguity-types)
    """
    gender_list = []
    number_pairs = []
    others = []
    for title in tqdm(entry_dict.keys()):
        # find pairs with number-ambiguity
        if "plural" in entry_dict[title].keys():
            plural = entry_dict[title]["plural"]
            for item in plural:
                if item in entry_dict.keys() and entry_dict[item] != entry_dict[title]: # when plural has an own entry, which is not the current entry (when plural is written the same as singular)
                    number_pairs.append((title,item)) # add all pairs of singular and plural with own sense to list
        # find words with more than one gender-possibility
        if "gender" in entry_dict[title].keys(): # German and Spanish
            gender = entry_dict[title]["gender"]
            if len(gender) > 1:
                gender_list.append(title)
        # collect words that have neither type of ambiguity
        if title not in gender_list: # if title has no gender-ambiguity
            if any([title in item for item in number_pairs]): 
                continue # when title has number-ambiguity, we don't need it here
            others.append(title)# only continues here when title has no gender- or number-ambiguity
    return (number_pairs,gender_list,others)

if __name__ == "__main__":
    language = input("Choose a language: German/Spanish/English \n ").lower()
    shorts = {"german":"de","english":"en","spanish":"es"}
    if language not in ["german","spanish","english"]:
        print(language + " is not supported.")
        sys.exit()
    if "win" in sys.platform:
        filename = language + "_wiktionary\\wiktionaries\\" + shorts[language] + "wiktionary-new.txt"
    elif "linux" in sys.platform:
        filename = language + "_wiktionary/wiktionaries/" + shorts[language] + "wiktionary-new.txt"
    else:
        print(sys.platform," is not supported.")
    print("Reading file...")
    entry_dict = read_files(filename)
    print("Finding relevant data...")
    (number_pairs,gender_list,others) = find_sets(entry_dict)