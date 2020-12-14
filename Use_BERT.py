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

def get_marked_text_from_examples(sentence):
    # get example sentences with special tokens for beginning and end of sentences
    return "[CLS] " + sentence + " [SEP]"

def run_BERT(word,tokenizer ,text, model):
    # print(word,text)
    word_position = text.split().index(word) + 1
    # Split the sentence into tokens.
    tokenized_text = tokenizer.tokenize(text)
    # Map the token strings to their vocabulary indeces.
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
    # print(indexed_tokens)

    tokens_tensor = torch.tensor([indexed_tokens])
    # print(tokens_tensor)
    # Mark each of the tokens as belonging to sentence 1
    segments_ids = [1] * len(tokenized_text)
    # print(segments_ids)
    # Convert inputs to PyTorch tensors
    segments_tensors = torch.tensor([segments_ids])
    # print(segments_tensors)
    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()
    # Predict hidden states features for each layer
    with torch.no_grad():
        encoded_layers, _ = model(tokens_tensor, segments_tensors)
        # print(encoded_layers)
    layer_word = 0

    batch_word = 0

    token_word = 0

    # For the 5th token in our sentence, select its feature values from layer.
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
        
        # `token` is a [12 x 768] tensor

        # Concatenate the vectors (that is, append them together) from the last 
        # four layers.
        # Each layer vector is 768 values, so `cat_vec` is length 3,072.
        cat_vec = torch.cat((token[-1], token[-2], token[-3], token[-4]), dim=0)
        
        # # Use `cat_vec` to represent `token`.
        token_vecs_cat.append(cat_vec)

    # sentence vector
    token_vecs = encoded_layers[11][0]
    # Calculate the average of all token vectors.
    sentence_embedding = torch.mean(token_vecs, dim=0)
    return (vec_word,sentence_embedding)

def process_number(relevant_pairs,entry_dict,model,tokenizer,frame):
    print("Calculating embeddings...")
    for (singular,plural) in tqdm(relevant_pairs):
        word_examples = entry_dict[singular]["examples"]
        plural_examples = entry_dict[plural]["examples"]
        word_senses = entry_dict[singular]["senses"]
        plural_senses = entry_dict[plural]["senses"]
        for w_index in word_senses.keys():
            sense = word_senses[w_index]
            for example in word_examples[w_index]:
                marked_text = get_marked_text_from_examples(example)
                if singular in marked_text.split():
                    (word_vector,sentence_embedding) = run_BERT(singular,tokenizer,marked_text,model)
                else:
                    continue
                frame = frame.append({"Word":singular,"Number":"Sg","Sense":sense,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
        for p_index in plural_senses.keys():
            sense = plural_senses[p_index]
            for example in plural_examples[p_index]:
                marked_text = get_marked_text_from_examples(example)
                if plural in marked_text.split():
                    (word_vector,sentence_embedding) = run_BERT(plural,tokenizer,marked_text,model)
                else:
                    continue
                frame = frame.append({"Word":plural,"Number":"Pl","Sense":sense,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
    return frame

def process_gender(language,gender_list,entry_dict,model,tokenizer,frame):
    print("Calculating embeddings...")
    for item in tqdm(gender_list):
        examples = entry_dict[item]["examples"]
        gender = entry_dict[item]["gender"]
        if language == "German": # because flections are only saved for German by now
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
                    elif language == "German" and any([f in marked_text.split() for f in flections]):
                        for f in flections:
                            if f in marked_text.split():
                                (word_vector,sentence_embedding) = run_BERT(f,tokenizer,marked_text,model)
                                break
                    else:
                        continue
                    frame = frame.append({"Word":item,"Gender":g,"Sense":current,"Sentence":sentence,"Word Vector":word_vector,"Sentence Vector":sentence_embedding},ignore_index=True)
    return frame

def process_other(other,entry_dict,model,tokenizer,frame):
    print("Calculating embeddings...")
    for item in tqdm(other):
        examples = entry_dict[item]["examples"]
        senses = entry_dict[item]["senses"]
        for index in senses.keys():
            sense = senses[index]
            for example in examples[index]:
                marked_text = get_marked_text_from_examples(example)
                if item in marked_text.split():
                    (word_vector,sentence_embedding) = run_BERT(item,tokenizer,marked_text,model)
                else:
                    continue
                frame = frame.append({"Word":item,"Sense":sense,"Sentence":example,"Word Vector":word_vector,"Sentence Vector":sentence_embedding},ignore_index=True)
    return frame

def write_files(language,path,filename,tokenizer,model,mode):
    print("Reading file...")
    entry_dict = read_files(filename)
    print(len(entry_dict.keys()))
    print("Getting data...")
    relevant_pairs,gender_list,other = find_sets(entry_dict)
    frame = pd.DataFrame(columns=["Word", "Number", "Gender", "Sense", "Sentence", "Word Vector", "Sentence Vector"])
    if mode == "-n": # for number
        frame = process_number(relevant_pairs,entry_dict,model,tokenizer,frame)
        frame.to_csv(path + "number.csv",sep="\t")
        frame.to_pickle(path + "number.pkl")
    elif mode == "-g" and language != "English": # for gender
        frame = process_gender(language,gender_list,entry_dict,model,tokenizer,frame)
        frame.to_csv(path + "gender.csv",sep="\t")
        frame.to_pickle(path + "gender.pkl")
    elif mode == "-o": # for other
        frame = process_other(other,entry_dict,model,tokenizer,frame)
        frame.to_csv(path + "other.csv",sep="\t")
        frame.to_pickle(path + "other.pkl")
    else:
        print("Invalid mode. Please choose from <-n,-o> for English, or from <-n,-g,-o> for Spanish and German.")
        sys.exit()

if __name__ == "__main__":
    language = sys.argv[2]
    if language.lower() == "english":
        path = "english_wiktionary\\wiktionaries\\"
        filename = path + "enwiktionary-new.txt"
        outpath = "english_wiktionary\\"
    elif language.lower() == "german":
        path = "german_wiktionary\\wiktionaries\\"
        filename = path + "dewiktionary-new.txt"
        outpath = "german_wiktionary\\"
    elif language.lower() == "spanish":
        path = "spanish_wiktionary\\wiktionaries\\"
        filename = path + "eswiktionary-new.txt"
        outpath = "spanish_wiktionary\\"
    else:
        print(language, " not available.")
        sys.exit()
    # Load tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    # Load pre-trained model (weights)
    model = BertModel.from_pretrained('bert-base-uncased')
    write_files(language,outpath,filename,tokenizer,model,sys.argv[1])
    