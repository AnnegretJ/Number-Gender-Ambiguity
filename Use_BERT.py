# -*- coding: utf-8 -*-
"""
Last Updated on Sun December 10 17:29 2020

@author: Annegret
"""


import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM
import pandas as pd # for building the file
from preprocessing import *
import sys
from tqdm import tqdm
import numpy as np
from transformers import AutoTokenizer, AutoModelForMaskedLM, BertForMaskedLM, BertTokenizer

def get_marked_text_from_examples(sentence):
    """
    get example sentences with special tokens for beginning and end of sentences\n
    ;param sentence: (str) sentence that needs to be marked\n
    ;returns: marked sentence\n
    """
    return "[CLS] " + sentence + " [SEP]"

def run_BERT(word,tokenizer ,text, model):
    """
    calculate word- and sentence-embeddings for a given word and sentence\n
    ;param word: (str) the word to calculate embeddings for\n
    ;param tokenizer: BertTokenizer\n
    ;param text: (str) example sentence used for context\n
    ;param model: specified BERT-model\n
    ;returns: tuple (word-embedding,sentence-embedding)
    """
    word_position = text.split().index(word) + 1
    # Split the sentence into tokens.
    tokenized_text = tokenizer.tokenize(text)
    # Map the token strings to their vocabulary indeces.
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    tokens_tensor = torch.tensor([indexed_tokens])
    # Mark each of the tokens as belonging to sentence 1
    segments_ids = [1] * len(tokenized_text)
    # Convert inputs to PyTorch tensors
    segments_tensors = torch.tensor([segments_ids])
    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()
    # Predict hidden states features for each layer
    with torch.no_grad():
        try:
            encoded_layers, _ = model(tokens_tensor, segments_tensors)
        except RuntimeError:
            return (None,None)
    layer_word = 0
    batch_word = 0
    token_word = 0
    token_word = word_position
    layer_word = word_position
    try:
        vec_word = encoded_layers[layer_word][batch_word][token_word]
    except IndexError:
        vec_word = np.nan
    # `encoded_layers` is a Python list.
    # Each layer in the list is a torch tensor.
    # Concatenate the tensors for all layers. We use `stack` here to
    # create a new dimension in the tensor.
    token_embeddings = torch.stack(encoded_layers, dim=0)
    # Remove dimension 1, the "batches".
    token_embeddings = torch.squeeze(token_embeddings, dim=1)
    # Swap dimensions 0 and 1.
    token_embeddings = token_embeddings.permute(1,0,2)
    # Stores the token vectors, with shape [22 x 3,072]
    token_vecs_cat = []
    # For each token in the sentence...
    for token in token_embeddings:
        # Concatenate the vectors from the last four layers.
        cat_vec = torch.cat((token[-1], token[-2], token[-3], token[-4]), dim=0)
        # # Use `cat_vec` to represent `token`.
        token_vecs_cat.append(cat_vec)
    # sentence vector
    token_vecs = encoded_layers[11][0]
    # Calculate the average of all token vectors.
    sentence_embedding = torch.mean(token_vecs, dim=0)
    return (vec_word,sentence_embedding)

def process_number(relevant_pairs,entry_dict,model,tokenizer,frame):
    """
    Process data on number-ambiguity-data and run through BERT\n
    ;param language: (str) specified language (supports English,German,Spanish)\n
    ;param relevant_pairs: (list) list containing tuples of sg-pl-pairs\n
    ;param entry_dict: (dict) dictionary containing all relevant information\n
    ;param model: specified BERT-model\n
    ;param tokenizer: BertTokenizer\n
    ;param frame: pandas dataframe for file-output\n
    ;returns: pandas dataframe containing all calculated vectors
    """
    print("Calculating number-ambiguity embeddings...")
    for (singular,plural) in tqdm(relevant_pairs):
        word_examples = entry_dict[singular]["examples"]
        plural_examples = entry_dict[plural]["examples"]
        word_senses = entry_dict[singular]["senses"]
        plural_senses = entry_dict[plural]["senses"]
        sg_flections = entry_dict[singular]["flection"]
        pl_flections = entry_dict[plural]["flection"]
        # calculate embeddings for singular-terms
        for key in word_senses.keys():
            for w_index in word_senses[key].keys():
                sense = word_senses[key][w_index]
                for example in word_examples[w_index]:
                    marked_text = get_marked_text_from_examples(example)
                    if singular in marked_text.split():
                        (word_vector,sentence_embedding) = run_BERT(singular,tokenizer,marked_text,model)
                    # when the word does not occur in a sentence, maybe an inflected form does
                    elif any([f in marked_text.split() for f in sg_flections]):
                        for f in sg_flections:
                            if f in marked_text.split():
                                (word_vector,sentence_embedding) = run_BERT(f,tokenizer,marked_text,model)
                                break
                    else:
                        continue
                    frame = frame.append({"Word":singular,"Number":"Sg","Gender":entry_dict[singular]["gender"],"Sense":sense,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
        # calculate embeddings for plural-terms
        for p_key in plural_senses.keys():
            for p_index in plural_senses[p_key].keys():
                sense = plural_senses[p_key][p_index]
                for example in plural_examples[p_index]:
                    marked_text = get_marked_text_from_examples(example)
                    if plural in marked_text.split():
                        (word_vector,sentence_embedding) = run_BERT(plural,tokenizer,marked_text,model)
                    elif any([f in marked_text.split() for f in pl_flections]):
                        for f in pl_flections:
                            if f in marked_text.split():
                                (word_vector,sentence_embedding) = run_BERT(f,tokenizer,marked_text,model)
                                break
                    else:
                        continue
                    frame = frame.append({"Word":plural,"Number":"Pl","Gender":entry_dict[plural]["gender"],"Sense":sense,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
    return frame

def process_gender(gender_list,entry_dict,model,tokenizer,frame):
    """
    Process data on gender-ambiguity-data and run through BERT\n
    ;param language: (str) specified language (supports English,German,Spanish)\n
    ;param gender_list: (list) list containing words that have more than one grammatical gender\n
    ;param entry_dict: (dict) dictionary containing all relevant information\n
    ;param model: specified BERT-model\n
    ;param tokenizer: BertTokenizer\n
    ;param frame: pandas dataframe for file-output\n
    ;returns: pandas dataframe containing all calculated vectors
    """
    print("Calculating gender-ambiguity embeddings...")
    for item in tqdm(gender_list):
        examples = entry_dict[item]["examples"]
        gender = entry_dict[item]["gender"]
        flections = entry_dict[item]["flection"]
        for g in gender:
            senses = entry_dict[item]["senses"][g]
            for index in senses:
                current = senses[index]
                sentences = examples[index]
                for sentence in sentences:
                    marked_text = get_marked_text_from_examples(sentence)
                    if item in marked_text.split():
                        (word_vector,sentence_embedding) = run_BERT(item,tokenizer,marked_text,model)
                    # check if inflections of word occur in the sentence
                    elif any([f in marked_text.split() for f in flections]):
                        for f in flections:
                            if f in marked_text.split():
                                (word_vector,sentence_embedding) = run_BERT(f,tokenizer,marked_text,model)
                                break
                    else:
                        continue
                    frame = frame.append({"Word":item,"Gender":g,"Sense":current,"Sentence":sentence,"Word Vector":word_vector,"Sentence Vector":sentence_embedding},ignore_index=True)
    return frame

def process_other(other,entry_dict,model,tokenizer,frame):
    """
    Process data on non-ambiguity-data and run through BERT\n
    ;param language: (str) specified language (supports English,German,Spanish)\n
    ;param other: (list) list containing all words without number- or gender-ambiguity\n
    ;param entry_dict: (dict) dictionary containing all relevant information\n
    ;param model: specified BERT-model\n
    ;param tokenizer: BertTokenizer\n
    ;param frame: pandas dataframe for file-output\n
    ;returns: pandas dataframe containing all calculated vectors
    """
    print("Calculating non-ambiguity embeddings...")
    for item in tqdm(other):
        examples = entry_dict[item]["examples"]
        senses = entry_dict[item]["senses"]
        flections = entry_dict[item]["flection"]
        for key in senses.keys():
            for index in senses[key].keys():
                sense = senses[key][index]
                for example in examples[index]:
                    marked_text = get_marked_text_from_examples(example)
                    if item in marked_text.split():
                        (word_vector,sentence_embedding) = run_BERT(item,tokenizer,marked_text,model)
                    # check if inflection of word occurs in sentence
                    elif any([f in marked_text.split() for f in flections]):
                        for f in flections:
                            if f in marked_text.split():
                                (word_vector,sentence_embedding) = run_BERT(f,tokenizer,marked_text,model)
                                break
                    else:
                        continue
                    frame = frame.append({"Word":item,"Gender":entry_dict[item]["gender"],"Sense":sense,"Sentence":example,"Word Vector":word_vector,"Sentence Vector":sentence_embedding},ignore_index=True)
    return frame

def write_files(language,path,filename,tokenizer,model):
    """
    write dataframes to files\n
    ;param language: specified language (supports English,German,Spanish)\n
    ;param path: path for output-file\n
    ;param filename: name of input-file\n
    ;param tokenizer: BertTokenizern\n
    ;param model: specified BERT-model\n
    ;returns: files containing pandas dataframes for each type of data in .csv and .pkl format\n
    """
    print("Reading file...")
    entry_dict = read_files(filename)
    print("Getting data...")
    relevant_pairs,gender_list,other = find_sets(entry_dict)
    number = pd.DataFrame(columns=["Word", "Number", "Gender", "Sense", "Sentence", "Word Vector", "Sentence Vector"])
    number = process_number(relevant_pairs,entry_dict,model,tokenizer,number)
    number.to_csv(path + "number.csv",sep="\t")
    number.to_pickle(path + "number.pkl")
    no_ambiguity = pd.DataFrame(columns=["Word", "Number", "Gender", "Sense", "Sentence", "Word Vector", "Sentence Vector"])
    no_ambiguity = process_other(other,entry_dict,model,tokenizer,no_ambiguity)
    no_ambiguity.to_csv(path + "other.csv",sep="\t")
    no_ambiguity.to_pickle(path + "other.pkl")
    if language.lower() != "english":
        gender = pd.DataFrame(columns=["Word", "Number", "Gender", "Sense", "Sentence", "Word Vector", "Sentence Vector"])
        gender = process_gender(gender_list,entry_dict,model,tokenizer,gender)
        gender.to_csv(path + "gender.csv", sep="\t")
        gender.to_pickle(path + "gender.pkl")

if __name__ == "__main__":
    language = sys.argv[1].lower()
    if language not in ["german","spanish","english"]:
        print(language + " is not supported.")
        sys.exit()
    elif language == "german":
        tokenizer = AutoTokenizer.from_pretrained("bert-base-german-cased")
        model = AutoModelForMaskedLM.from_pretrained("bert-base-german-cased")
    elif language == "spanish":
        tokenizer = BertTokenizer.from_pretrained("pytorch/", do_lower_case=False)
        model = BertForMaskedLM.from_pretrained("pytorch/")
    # elif language in ["german","spanish"]:
    #     model = BertModel.from_pretrained("bert-base-multilingual-uncased")
    #     tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-uncased")
    else:
        model = BertModel.from_pretrained("bert-base-uncased")
        tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    shorts = {"german":"de","spanish":"es","english":"en"}
    if "win" in sys.platform:
        filename = language + "_wiktionary\\wiktionaries\\" + shorts[language] + "wiktionary-new.txt"
        outpath = language + "_wiktionary\\"
    elif "linux" in sys.platform:
        filename = language + "_wiktionary/wiktionaries/" + shorts[language] + "wiktionary-new.txt"
        outpath = language + "_wiktionary\\"
    else:
        print(sys.platform," is not supported.")
    # Load pre-trained model (weights)
    write_files(language,outpath,filename,tokenizer,model)
    