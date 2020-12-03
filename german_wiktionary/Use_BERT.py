# -*- coding: utf-8 -*-
"""
Last Updated on Sun Jul 05 18:52 2020

@author: Annegret
"""


import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM
import pandas as pd # for building the file
from de_preprocessing import *
import numpy as np

def get_marked_text_from_examples(sentence):
    # get example sentences with special tokens for beginning and end of sentences
    return "[CLS] " + sentence + " [SEP]"

def run_BERT(word,entries,tokenizer ,text, model):
    if word not in text.split(): # when for some reason there is still a sentence that does not contain the word
        if "flection" in entries[word].keys():
            all_items = []
            for item in entries[word].keys(): # check if any of the inflected forms occur in the sentence
                if item in text.split():
                    word = item
                    all_items.append(False) # append False when item is in sentence
                    break
                else:
                    all_items.append(True) # append True when item is not in sentence
            if all(all_items):
                raise TypeError
        else:
            return # stop iteration on this sentence (only happens when neither word nor inflection occur in the sentence)
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

def process_number(number_pairs,entry_dict):
    frame = pd.DataFrame(columns=["Word", "Number", 'Gender','Sense', 'Sentence',"Word Vector", "Sentence Vector"])
    for (singular,plural) in number_pairs:
        if "examples" not in entry_dict[singular].keys() or "examples" not in entry_dict[plural].keys(): # only use number-pairs where both words have example sentences
            continue
        for gender in entry_dict[singular]["senses"].keys():
            singular_examples = entry_dict[singular]["examples"] # dict index - sentence
            plural_examples = entry_dict[plural]["examples"] # dict index - sentence
            singular_senses = entry_dict[singular]["senses"][gender] # dict index - sense
            if gender in entry_dict[plural]["senses"].keys():
                plural_senses = entry_dict[plural]["senses"][gender] # dict index - sense
            else:
                for other in entry_dict[plural]["senses"].keys(): # plurals usually have one or no plurals
                    plural_senses = entry_dict[plural]["senses"][other]
            for sg_index in singular_examples.keys():
                try:
                    sg_sense = singular_senses[sg_index]
                except KeyError:
                    continue
                for pl_index in plural_examples.keys():
                    if singular_examples[sg_index] == [] or plural_examples[pl_index] == []:  # when one of them has no examples, there is no comparison possible
                        continue
                    try:
                        pl_sense = plural_senses[pl_index]
                    except KeyError:
                        continue
                    for example in singular_examples[sg_index]:
                        marked_text = get_marked_text_from_examples(example)
                        try:
                            for i in range(0,len(frame["Sense"])):
                                if sg_sense == frame["Sense"][i]: # to make sure every sense only occurs once
                                    raise TypeError # raise Error that is going to be caught later anyway
                            (word_vector,sentence_embedding) = run_BERT(singular,entry_dict,tokenizer,example,model)
                            frame = frame.append({"Word":singular,"Number":"singular","Gender":gender,"Sense":sg_sense,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                            print(singular)
                        except TypeError:
                            continue
                    for example in plural_examples[pl_index]:
                        marked_text = get_marked_text_from_examples(example)
                        try:
                            for i in range(0,len(frame["Sense"])):
                                if pl_sense == frame["Sense"][i]:
                                    raise TypeError
                            (word_vector,sentence_embedding) = run_BERT(plural,entry_dict,tokenizer,example,model)
                            frame = frame.append({"Word":plural,"Number":"plural","Gender":gender,"Sense":pl_sense,"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                            print(plural)
                        except TypeError:
                            continue
    frame.to_csv("number.csv",sep="\t")
    frame.to_pickle("number.pkl")

def process_gender(gender_list,entry_dict):
    frame = pd.DataFrame(columns=["Word", "Number", 'Gender','Sense', 'Sentence',"Word Vector", "Sentence Vector"])
    for word in gender_list:
        # print(entry_dict["Kiefer"])
        # exit()
        if "examples" not in entry_dict[word].keys():
            continue
        for gender in entry_dict[word]["gender"]:
            # if word == "Kiefer":
            #     print(gender)
            examples = entry_dict[word]["examples"]
            senses = entry_dict[word]["senses"][gender]
            for index in examples.keys():
                # if word == "Kiefer":
                #     print(index)
                if examples[index] == []:
                    continue
                for example in examples[index]:
                    # if word == "Kiefer":
                    #     print(example)
                    marked_text = get_marked_text_from_examples(example)
                    try:
                        if index in senses.keys():
                            # if word == "Kiefer":
                            #     print(senses[index])
                            for i in range(0,len(frame["Sense"])):
                                if senses[index] == frame["Sense"][i]: # when the sense already occurs in frame
                                    raise TypeError
                        # if word == "Kiefer":
                        #     print(example)
                        (word_vector,sentence_embedding) = run_BERT(word,entry_dict,tokenizer,example,model)
                        # if word == "Kiefer":
                        #     print(word, word_vector)
                        if index in senses.keys():
                            frame = frame.append({"Word":word,"Number":"singular","Gender":gender,"Sense":senses[index],"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                        else:
                            frame = frame.append({"Word":word,"Number":"singular","Gender":gender,"Sense":"-","Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                        print(word)
                    except TypeError:
                        continue
    frame.to_csv("gender.csv",sep="\t")
    frame.to_pickle("gender.pkl")

def process_no_ambiguity(others,entry_dict): # calculate embedding-vectors for words without these specific ambiguities
    # these vectors are saved in a separate file
    frame = pd.DataFrame(columns=["Word", "Number", 'Gender','Sense', 'Sentence',"Word Vector", "Sentence Vector"])
    for word in others:
        if "examples" not in entry_dict[word].keys():
            continue
        for gender in entry_dict[word]["gender"]:
            examples = entry_dict[word]["examples"]
            senses = entry_dict[word]["senses"][gender]
            for index in examples.keys():
                if examples[index] == []:
                    continue
                for example in examples[index]:
                    marked_text = get_marked_text_from_examples(example)
                    try:
                        if index in senses.keys():
                            for i in range(0,len(frame["Sense"])):
                                if senses[index] == frame["Sense"][i]: # when the sense already occurs in frame
                                    raise TypeError
                        (word_vector,sentence_embedding) = run_BERT(word,entry_dict,tokenizer,example,model)
                        if index in senses.keys():
                            frame = frame.append({"Word":word,"Number":"singular","Gender":gender,"Sense":senses[index],"Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                        else:
                            frame = frame.append({"Word":word,"Number":"singular","Gender":gender,"Sense":"-","Sentence":example,"Word Vector": word_vector, "Sentence Vector": sentence_embedding},ignore_index=True)
                        print(word)
                    except TypeError:
                        continue
    frame.to_csv("other.csv",sep="\t")
    frame.to_pickle("other.pkl")


if __name__ == "__main__":
    entry_dict = read_files()
    (number_pairs,gender_list,others) = find_sets(entry_dict)
    # new_examples = examples(relevant_pairs)
    # Load tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    # Load pre-trained model (weights)
    model = BertModel.from_pretrained('bert-base-multilingual-cased')
    process_number(number_pairs,entry_dict)
    process_gender(gender_list,entry_dict)
    # process_no_ambiguity(others,entry_dict)
    
    

 