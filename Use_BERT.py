# -*- coding: utf-8 -*-
"""
Last Updated on Sun Jul 05 18:52 2020

@author: Annegret
"""


import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM
import pandas as pd # for building the file
from preprocessing import *
import sys

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

    tokens_tensor = torch.tensor([indexed_tokens])
    # Mark each of the tokens as belonging to sentence 1
    segments_ids = [1] * len(tokenized_text)
    # Convert inputs to PyTorch tensors
    segments_tensors = torch.tensor([segments_ids])
    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()
    # Predict hidden states features for each layer
    with torch.no_grad():
        encoded_layers, _ = model(tokens_tensor, segments_tensors)
        
    layer_word = 0

    batch_word = 0

    token_word = 0

    # For the 5th token in our sentence, select its feature values from layer.
    token_word = word_position
    layer_word = word_position
    try:
        vec_word = encoded_layers[layer_word][batch_word][token_word]
    except IndexError:
        vec_word = "IndexError"

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
    for (singular,plural) in relevant_pairs:
        # print(singular)
        word_examples = entry_dict[singular]["examples"]
        plural_examples = entry_dict[plural]["examples"]
        # if word_examples == [] or plural_examples == []:
        #     continue
        for first in word_examples.keys():
            for second in plural_examples.keys():
                if word_examples[first] == [] or plural_examples[second] == []:
                    continue
                for example in word_examples[first]:
                    marked_text = get_marked_text_from_examples(example)
                    if singular in marked_text.split():
                        (word_vector,sentence_embedding) = run_BERT(singular,tokenizer,marked_text,model)
                    else:
                        continue
                    frame = frame.append({"Word":singular,"Number":"Sg","Sense":first,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                    print(singular)
#         for sense in plural_examples.keys():
                for example in plural_examples[second]:
                    marked_text = get_marked_text_from_examples(example)
                    if plural in marked_text.split():
                        (word_vector,sentence_embedding) = run_BERT(plural,tokenizer,marked_text,model)
                    else:
                        continue
                    frame = frame.append({"Word":plural,"Number":"Pl","Sense":second,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                    print(plural)
    return frame

def process_other(other,entry_dict,model,tokenizer,frame):
    for item in other:
        examples = entry_dict[item]["examples"]
        for sense in examples.keys():
            if examples[sense] == []:
                continue
        for example in examples[sense]:
            marked_text = get_marked_text_from_examples(example)
            if item in marked_text.split():
                (word_vector,sentence_embedding) = run_BERT(item,tokenizer,marked_text,model)
            else:
                continue
            frame = frame.append({"Word":item,"Sense":sense,"Sentence":example,"Word Vector":word_vector,"Sentence Vector":sentence_embedding},ignore_index=True)
            print(item)
    return frame

if __name__ == "__main__":
    entry_dict = read_files()
    relevant_pairs,other = find_pairs(entry_dict)
    # Load tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    # Load pre-trained model (weights)
    model = BertModel.from_pretrained('bert-base-uncased')
    # for English:
    # frame = pd.DataFrame(columns=["Word", 'Sg/Pl','Sense', 'Sentence',"Word Vector", "Sentence Vector"])
    # for German:
    frame = pd.DataFrame(columns=["Word", "Number", "Gender", "Sense", "Sentence", "Word Vector", "Sentence Vector"])
    if sys.argv[1] == "-n": # for number
        frame = process_number(relevant_pairs,entry_dict,model,tokenizer,frame)
        frame.to_csv("number.csv",sep="\t")
        frame.to_pickle("number.pkl")
    elif sys.argv[1] == "-o": # for other
        frame = process_other(other,entry_dict,model,tokenizer,frame)
        frame.to_csv("other.csv",sep="\t")
        frame.to_pickle("other.pkl")