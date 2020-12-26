import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from sklearn.manifold import TSNE
import torch
import sys
import numpy as np
import os

# import tensorflow as tf
def tsne_plot(model,facts,show_examples=False): # word,sense - vector
    "Creates a TSNE model and plots it"
    labels = []
    labels_averages = []
    tokens = []
    tokens_averages = []
    handles = []
    handles_averages = []
    for (word,sense) in model.keys():
        sum_of_vectors = np.empty(shape=len(model[(word,sense)]))
        counter = 0
        for item in model[(word,sense)]: # for every individual embedding vector
            counter += 1
            sum_of_vectors = np.add(sum_of_vectors,item)
        
        tokens.append(np.array(sum_of_vectors/counter))
        labels.append(word)
        handles.append(str(word) + " " + str(sense) + str(facts[(word,sense)][0]))
        # tokens.append(model[(word,sense)]) # embedding-vectors
        # labels.append(word)
        if counter > 1: # when there are more than one examples for the current pair of word-sense
            tokens_averages.append(np.array(sum_of_vectors)/counter) # vector for all example senses in this sense
            labels_averages.append(word) # word according to above vector
            handles_averages.append("Average of " + str(word) + " " + str(sense) + str(facts[(word,sense)][0]))
        if show_examples:
            try:
                handles.append(str(word) + " " + str(sense) + str(facts[(word,sense)][0]) + str(facts[(word,sense)][1]))
            except KeyError:
                handles.append(str(word) + " " + str(sense))
        else:
            try:
                handles.append(str(word) + " " + str(sense) + str(facts[(word,sense)][0]))
            except KeyError:
                handles.append(str(word) + " " + str(sense))
    tsne_model = TSNE(perplexity=40, n_components=3, init='pca', n_iter=2500, random_state=23,)
    if len(tokens) > 1:
        new_values = tsne_model.fit_transform(tokens)
    else:
        new_values = tokens # this occurs when there is only one point to be presented
    if len(tokens_averages) > 1:
        new_values_averages = tsne_model.fit_transform(tokens_averages)
    else:
        new_values_averages = tokens_averages
    x = []
    y = []
    z = []
    for value in new_values:
        x.append(value[0])
        y.append(value[1])
        z.append(value[2])
    fig = plt.figure()
    ax = fig.add_subplot(111,projection="3d")
    c = list(range(len(x)))
    # use colormap without faded colors (more useful for 2-dimensional view of 3-dimensional plots)
    scatter = ax.scatter(x,y,z, c=c, cmap='Set1')
    for i in range(len(x)):
        ax.annotate(labels[i],
                     xy=(x[i], y[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')
    plot_handles, _ = scatter.legend_elements()
    for i in range(new_values_averages):
        average_scatter = ax.scatter(new_values_averages[i][0],new_values_averages[i][1], c=c, cmap="Set1",marker="*")
    other_handles,_ = average_scatter.legend_elements()
    # l = ax.legend(plot_handles, handles=handles+handles_averages,bbox_to_anchor=(-0.3, 1),
    #             loc="best", title="Senses",mode="expand",borderaxespad=0.)
    l = ax.legend(handles=handles+handles_averages,bbox_to_anchor=(-0.3,1),loc="best",title="Senses",mode="expand",borderaxespad=0.)
    # x_average = []
    # y_average = []
    # z_average = []
    # for value in new_values_averages:
    #     x_average.append(value[0])
    #     y_average.append(value[1])
    #     z_average.append(value[2])
    # scatter_averages = ax.scatter(x,y,z,c=c,cmap="Set1",marker="*")
    # for i in range(len(x)):
    #     ax.annotate(labels_averages[i],
    #                  xy=(x[i],y[i]),
    #                  xytext=(5,2),
    #                  textcoords='offset points',
    #                  ha='right',
    #                  va='bottom')
    # plot_handles,_ = scatter.legend_elements()
    # l = ax.legend(plot_handles,handles_averages,bbox_to_anchor=(-0.1,1),loc="best",title="Senses",mode="expand",borderaxespad=0.)
    plt.tight_layout(pad = 1.4, w_pad = 1.4, h_pad = 1.4)
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.show()


def read_files(file_1,mode_1="pkl",file_2=None,mode_2="pkl",file_3=None,mode_3="pkl"):
    if mode_1 == "pkl":
        data = pd.read_pickle(file_1)
    elif mode_1 == "csv":
        data = pd.read_csv(file_1)
    else:
        print("Unsupported mode for file_1: ", mode_1)
    if file_2 != None:
        if mode_2 == "pkl":
            second = pd.read_pickle(file_2)
        elif mode_2 == "csv":
            second = pd.read_csv(file_2)
        else:
            print("Unsupported mode for file_2: ", mode_2)
        data = pd.merge(data,second,how="outer")
        data = data.reset_index()
    if file_3 != None:
        if mode_3 == "pkl":
            third = pd.read_pickle(file_3)
        elif mode_3 == "csv":
            third = pd.read_csv(file_3)
        else:
            print("Unsupported mode for file_3: ", mode_3)
        data = pd.merge(data,third,how="outer")
        data = data.reset_index()
    return data

def start(data,wordlist):
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
            number = "number: " + str(data["Number"][index])
            example = "example: " + data["Sentence"][index]
            word_facts[(word,data["Sense"][index])] = [number,example] # store facts for later
            word_vectors[(word,data["Sense"][index])] = word_vector
    if len(word_vectors.keys()) != 0:
        answer = input("Show examples in legend? (Y/N) \n => ")
        while answer:
            if answer.lower() == "n":
                tsne_plot(word_vectors,word_facts)
                break
            elif answer.lower() == "y":
                tsne_plot(word_vectors,word_facts,show_examples=True)
                break
            else:
                print("Invalid Input. Show examples? (Y/N) \n => ")

if __name__ == "__main__":
    if "win" in sys.platform:
        win = True
    elif "linux" in sys.platform:
        win = False
    else:
        print(sys.platform, " is not supported.")
    category = sys.argv
    if len(category) > 3:
        print("Too many arguments.")
        exit()
    elif len(category) < 3:
        print("Missing argument")
        exit()
    else:
        item = category[1] # first item is file name
        language = category[2]
        mode_1 = "pkl"
        mode_2 = "pkl"
        mode_3 = "pkl"
        if win:
            if language.lower() == "english":
                path = "english_wiktionary\\"
            elif language.lower() == "german":
                path = "german_wiktionary\\"
            elif language.lower() == "spanish":
                path = "spanish_wiktionary\\"
            else:
                print("Language not found.")
                exit()
        else:
            if language.lower() == "english":
                path = "english_wiktionary/"
            elif language.lower() == "german":
                path = "german_wiktionary/"
            elif language.lower() == "spanish":
                path = "spanish_wiktionary/"
            else:
                print("Language not found.")
                exit()
        if item == "-n": # for number-ambiguity
            if os.path.exists(path + "number.pkl"):
                filename = path + "number.pkl"
            else:
                filename = path + "number.csv"
                mode_1 = "csv"
            data = read_files(filename,mode_1)
        elif item == "-g" and language.lower() != "english":
            if os.path.exists(path + "gender.pkl"):
                filename = path + "gender.pkl"
            else:
                filename = path + "gender.csv"
                mode_1 = "csv"
            data = read_files(filename,mode_1)
        elif item == "-ng" and language.lower() != "english":
            if os.path.exists(path + "number.pkl"):
                first = path + "number.pkl"
            else:
                first = path + "number.csv"
                mode_1 = "csv"
            if os.path.exists(path + "gender.pkl"):
                second = path + "gender.pkl"
            else:
                second = path + "gender.csv"
                mode_2 = "csv"
            data = read_files(first,mode_1,second,mode_2)
        elif item == "-o": # for all data except ambiguity-types
            if os.path.exists(path + "other.pkl"):
                filename = path + "other.pkl"
            else:
                filename = path + "other.csv"
                mode_1 = "csv"
            data = read_files(filename,mode_1)
        elif item == "-no":
            if os.path.exists(path + "number.pkl"):
                first = path + "number.pkl"
            else:
                first = path + "number.csv"
                mode_1 = "csv"
            if os.path.exists(path + "other.pkl"):
                second = path + "other.pkl"
            else:
                first = path + "other.csv"
                mode_2 = "csv"
            data = read_files(first,mode_1,second,mode_2)
        elif item == "-go" and language.lower() != "english":
            if os.path.exists(path + "gender.pkl"):
                first = path + "gender.pkl"
            else:
                first = path + "gender.csv"
                mode_1 = "csv"
            if os.path.exists(path + "other.pkl"):
                second = path + "other.pkl"
            else:
                second = path + "other.csv"
                mode_2 = "csv"
            data = read_files(first,mode_1,second,mode_2)
        elif item == "-a": # for all available data
            if os.path.exists(path + "number.pkl"):
                first = path + "number.pkl"
            else:
                first = path + "number.csv"
                mode_1 = "csv"
            if os.path.exists(path + "other.pkl"):
                second = path + "other.pkl"
            else:
                second = path + "other.csv"
                mode_2 = "csv"
            if language.lower() == "english":
                data = read_files(first,mode_1,second,mode_2)
            else:
                if os.path.exists(path + "gender.pkl"):
                    third = path + "gender.pkl"
                else:
                    third = path + "gender.csv"
                    mode_3 = "csv"
                data = read_files(first,mode_1,second,mode_2,third,mode_3)
        else:
            print("Invalid argument: " + item)
            exit()
    words = input("Which words do you want to see comparisons of? (Multiple words separated by whitespace) => ")
    wordlist = words.split() # get individual words
    start(data,wordlist)
        