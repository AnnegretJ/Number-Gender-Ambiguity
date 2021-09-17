import pandas as pd
import torch
import sys
import numpy as np
import os
from os.path import exists
import itertools
from scipy.spatial import distance
import ast

# import tensorflow as tf
def distances(model,path,mode): # word,sense - vector
    "Computes embedding vector distances"
#     tokens = []
#     tokens_averages = []
    all_vectors = dict()
    print([word for (word,sense) in model.keys()])
    for (word,sense) in model.keys():
        tokens = []
        tokens_averages = []
        value = model[(word,sense)]
        if np.isnan(value).any(): # when there is NaN in the array
            print("isnan")
            continue
        sum_of_vectors = np.empty(shape=len(value))
        counter = 0
        for item in value: # for every individual embedding vector for this sense
            counter += 1
            sum_of_vectors = np.add(sum_of_vectors,item)
        tokens.append(np.array(sum_of_vectors/counter))
        if counter > 1: # when there are more than one examples for the current pair of word-sense
            tokens_averages.append(np.array(sum_of_vectors)/counter) # vector for all example senses in this sense
            all_vectors[(word,sense)] = tokens_averages[-1] # the last added item
        else:
            all_vectors[(word,sense)] = tokens[-1] # when only one new item was added to tokens, add it as well
    print([word for (word,sense) in model.keys()])
    print("Create_files")
    print(len(all_vectors))
    with open(path+mode+"_cosine_distances.txt","w+") as cos:
        with open(path+mode+"_euclidean_distances.txt","w+") as euc:
            with open(path+mode+"_manhattan_distances.txt","w+") as man:
                for i in itertools.combinations(all_vectors.keys(),2): # all combinations of 2 vectors
                    get_distances(i[0],i[1],all_vectors[i[0]],all_vectors[i[1]],cos,euc,man)

def get_distances(first,second,first_vector,second_vector,cos,euc,man):
    print("distances")
    first_norm = np.linalg.norm(first_vector)
    second_norm = np.linalg.norm(second_vector)
    cos_text = "Cosine Distance between " + str(first) + str(second) + ": " + str(distance.cosine(first_norm,second_norm)) + "\n"
    print(cos_text)
    cos.write(cos_text)
    euc_text = "Euclidean Distance between " + str(first) + str(second) + ": " + str(distance.euclidean(first_norm,second_norm)) + "\n"
    euc.write(euc_text)
    man_text = "Manhattan Distance between " + str(first) + str(second) + ": " + str(distance.cityblock(first_vector,second_vector)) + "\n"
    man.write(man_text)

def read_files(list_1,list_2=None,list_3=None):
    data = pd.DataFrame(columns=["Word","Number","Gender","Sense","Sentence","Word Vector","Sentence Vector"])
    for item in list_1:
        current = pd.read_csv(item,sep="\t",header=0)
        data = pd.merge(data,current,how="outer")
        try:
            data = data.reset_index()
        except ValueError:
            pass
    if list_2 != None:
        for item in list_2:
            current = pd.read_csv(item,sep="\t",header=0)
            data = pd.merge(data,current,how="outer")
            data = data.reset_index()
    if list_3 != None:
        for item in list_3:
            current = pd.read_csv(item,sep="\t",header=0)
            data = pd.merge(data,current,how="outer")
            data = data.reset_index()
    return data

def start(data,wordlist,path,mode):
    word_vectors = dict()
    word_facts = dict()
    data = data.dropna(subset=['Word Vector']) # remove all rows that contain nan in word vector or sentence vector
    data = data.reset_index(drop=True)
    for word in wordlist:
        word_not_found = True # set to False when word is found
        # checking if the word is in the dataset
        for i in range(0,len(data["Word"])):
            if word == data["Word"][i]: # break loop if word is in dataset
                word_not_found = False
                break
        visited = []
        if word_not_found: # when the for-loop did not find the word in data
            print(word + " has not been found. Type 'Y' to skip this word, type 'N' to stop the iteration. Y/N")
            answer = input("=> ")
            while answer:
                if answer.lower() == "n":
                    exit()
                elif answer.lower() == "y":
                    break
                else:
                    answer = input("Invalid input. Please only type 'Y' or 'N': => ")
        else:
            # count entries in data (one entry = one sense)
            visited = []
            for i in range(0, len(data['Word'])):
                if word == data["Word"][i]:
                    visited.append(i) # store the index of this entry
                    continue
            print(visited)
            print(str(len(visited)) + " entries found for " + word)
        if visited:
            for index in visited:
                word_vector = torch.tensor(ast.literal_eval(data["Word Vector"][index])) # string to list to tensor
#                 word_vector = data["Word Vector"][index].tolist()
                word_vectors[(word,data["Sense"][index])] = word_vector
#                 print(data["Sense"][index])
    print([word for (word,sense) in word_vectors.keys()])
    if len(word_vectors.keys()) != 0:
#         print([word for (word,sense) in word_vectors.keys()])
        distances(word_vectors,path,mode)

if __name__ == "__main__":
    category = sys.argv
    if len(category) > 4:
        print("Too many arguments.")
        exit()
    elif len(category) < 4:
        print("Missing argument")
        exit()
    else:
        item = category[1] # first item is file name
        language = category[2]
        model_type = category[3].lower() # multilingual or specific
        if model_type not in ["specific","multilingual"]:
            print("Invalid type: ", model_type)
            sys.exit()
        if language.lower() == "english":
            path = "english_wiktionary/"+model_type+"/"
        elif language.lower() == "german":
            path = "german_wiktionary/"+model_type+"/"
        elif language.lower() == "spanish":
            path = "spanish_wiktionary/"+model_type+"/"
        else:
            print("Language not found.")
            exit()
        number = [path + "number.csv"]
        number_1 = path + "number_1.csv"
        number_2 = path + "number_2.csv"
        number_3 = path + "number_3.csv"
        if exists(number_1) and exists(number_2):
            if exists(number_3):
                number = [number_1,number_2,number_3]
            else:
                number = [number_1,number_2]
        gender = [path +  "gender.csv"]
        gender_1 = path + "gender_1.csv"
        gender_2 = path + "gender_2.csv"
        gender_3 = path + "gender_3.csv"
        if exists(gender_1) and exists(gender_2) and language.lower() != "english":
            if exists(gender_3):
                gender = [gender_1,gender_2,gender_3]
            else:
                gender = [gender_1,gender_2]
        other = [path + "other.csv"]
        other_1 = path + "other_1.csv"
        other_2 = path + "other_2.csv"
        other_3 = path + "other_3.csv"
        if exists(other_1) and exists(other_2):
            if exists(other_3):
                other = [other_1,other_2,other_3]
            else:
                other = [other_1,other_2]
        if item == "-n": # for number-ambiguity
            kind = "number"
            data = read_files(number)
        elif item == "-g" and language.lower() != "english":
            kind = "gender"
            data = read_files(gender)
        elif item == "-ng" and language.lower() != "english":
            kind = "number_gender"
            data = read_files(number,gender)
        elif item == "-o": # for all data except ambiguity-types
            kind = "other"
            data = read_files(other)
        elif item == "-no":
            kind = "number_other"
            data = read_files(number,other)
        elif item == "-go" and language.lower() != "english":
            kind = "gender_other"
            data = read_files(gender,other)
        elif item == "-a": # for all available data
            kind = "all"
            if language.lower() == "english":
                data = read_files(number,other)
            else:
                data = read_files(number,gender,other)
        else:
            print("Invalid argument: " + item)
            exit()
    words = input("Which words do you want to see comparisons of? (Multiple words separated by whitespace) => ")
    wordlist = words.split() # get individual words
    start(data,wordlist,path,kind)
