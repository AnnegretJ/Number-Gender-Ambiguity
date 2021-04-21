import pandas as pd
import torch
import sys
import numpy as np
import os
import itertools
from scipy.spatial import distance

# import tensorflow as tf
def distances(model,path,mode): # word,sense - vector
    "Computes embedding vector distances"
    tokens = []
    tokens_averages = []
    all_vectors = dict()
    for (word,sense) in model.keys():
        item = model[(word,sense)]
        if np.isnan(item).any(): # when there is NaN in the array
            continue
        sum_of_vectors = np.empty(shape=len(model[(word,sense)]))
        counter = 0
        for item in model[(word,sense)]: # for every individual embedding vector
            counter += 1
            sum_of_vectors = np.add(sum_of_vectors,item)
        tokens.append(np.array(sum_of_vectors/counter))
        if counter > 1: # when there are more than one examples for the current pair of word-sense
            tokens_averages.append(np.array(sum_of_vectors)/counter) # vector for all example senses in this sense
            all_vectors[word] = tokens_averages[-1] # the last added item
        else:
            all_vectors[word] = tokens[-1] # when only one new item was added to tokens, add it as well
    with open(path+mode+"_cosine_distances.txt","w+") as cos:
        with open(path+mode+"_euclidean_distances.txt","w+") as euc:
            with open(path+mode+"_manhattan_distances.txt","w+") as man:
                for i in itertools.combinations(all_vectors.keys(),2): # all combinations of 2 vectors
                    get_distances(i[0],i[1],all_vectors[i[0]],all_vectors[i[1]],cos,euc,man)

def get_distances(first,second,first_vector,second_vector,cos,euc,man):
    first_norm = np.linalg.norm(first_vector)
    second_norm = np.linalg.norm(second_vector)
    cos_text = "Cosine Distance between " + first + second + ": " + str(distance.cosine(first_norm,second_norm)) + "\n"
    cos.write(cos_text)
    euc_text = "Euclidean Distance between " + first + second + ": " + str(distance.euclidean(first_norm,second_norm)) + "\n"
    euc.write(euc_text)
    man_text = "Manhattan Distance between " + first + second + ": " + str(distance.cityblock(first_vector,second_vector)) + "\n"
    man.write(man_text)    

def read_files(file_1,file_2=None,file_3=None):
    data = pd.read_csv(file_1)
    if file_2 != None:
        second = pd.read_csv(file_2)
        data = pd.merge(data,second,how="outer")
        data = data.reset_index()
    if file_3 != None:
        third = pd.read_csv(file_3)
        data = pd.merge(data,third,how="outer")
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
            print(str(len(visited)) + " entries found for " + word)
        for index in visited:
            word_vector = data["Word Vector"][index].tolist()
            word_vectors[(word,data["Sense"][index])] = word_vector
    if len(word_vectors.keys()) != 0:
        answer = input("Show examples in legend? (Y/N) \n => ")
        while answer:
            if answer.lower() == "n":
                distances(word_vectors,path,mode)
                break
            elif answer.lower() == "y":
                distances(word_vectors,path,mode)
                break
            else:
                print("Invalid Input. Show examples? (Y/N) \n => ")

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
        if item == "-n": # for number-ambiguity
            kind = "number"
            filename = path + "number.csv"
            data = read_files(filename)
        elif item == "-g" and language.lower() != "english":
            kind = "gender"
            filename = path + "gender.csv"
            data = read_files(filename)
        elif item == "-ng" and language.lower() != "english":
            kind = "number_gender"
            first = path + "number.csv"
            second = path + "gender.csv"
            data = read_files(first,second)
        elif item == "-o": # for all data except ambiguity-types
            kind = "other"
            filename = path + "other.csv"
            data = read_files(filename)
        elif item == "-no":
            kind = "number_other"
            first = path + "number.csv"
            second = path + "other.csv"
            data = read_files(first,second)
        elif item == "-go" and language.lower() != "english":
            kind = "gender_other"
            first = path + "gender.csv"
            second = path + "other.csv"
            data = read_files(first,second)
        elif item == "-a": # for all available data
            kind = "all"
            first = path + "number.csv"
            second = path + "other.csv"
            if language.lower() == "english":
                data = read_files(first,second)
            else:
                third = path + "gender.csv"
                data = read_files(first,second,third)
        else:
            print("Invalid argument: " + item)
            exit()
    words = input("Which words do you want to see comparisons of? (Multiple words separated by whitespace) => ")
    wordlist = words.split() # get individual words
    start(data,wordlist,path,kind)
        