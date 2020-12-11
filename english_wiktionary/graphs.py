import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from sklearn.manifold import TSNE
import torch
import sys


# import tensorflow as tf
def tsne_plot(model,facts,show_examples=False): # word,sense - vector
    "Creates a TSNE model and plots it"
    labels = []
    tokens = []
    handles = []
    for (word,sense) in model.keys():
        tokens.append(model[(word,sense)])
        labels.append(word)
        if show_examples:
            try:
                handles.append(str(word) + " " + str(sense) + str(facts[(word,sense)][0]) + str(facts[(word,sense)][1]))
            except KeyError:
                handles.append(sense)
        else:
            try:
                handles.append(str(word) + " " + str(sense) + str(facts[(word,sense)][0]))
            except KeyError:
                handles.append(sense)
    tsne_model = TSNE(perplexity=40, n_components=3, init='pca', n_iter=2500, random_state=23,)
    new_values = tsne_model.fit_transform(tokens)
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
    scatter = ax.scatter(x,y,z, c=c)
    for i in range(len(x)):
        ax.annotate(labels[i],
                     xy=(x[i], y[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')
    plot_handles, _ = scatter.legend_elements()
    l = ax.legend(plot_handles, handles,bbox_to_anchor=(-0.1, 1),
                loc="best", title="Senses",mode="expand",borderaxespad=0.)
    plt.tight_layout(pad = 1.4, w_pad = 1.4, h_pad = 1.4)
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.show()

category = sys.argv
if len(category) > 2:
    print("Too many arguments.")
    exit()
elif len(category) < 2:
    print("Missing argument")
    exit()
else:
    item = category[1] # first item is file name
    if item == "-n": # for number-ambiguity
        data = pd.read_pickle("number.pkl")
    elif item == "-o": # for all data except ambiguity-types
        data = pd.read_pickle("other.pkl")
    elif item == "-a": # for all available data
        a = pd.read_pickle("number.pkl")
        b = pd.read_pickle("other.pkl")
        data = pd.merge(a,b,how="outer")
        data = data.reset_index()
    else:
        print("Invalid argument: " + item)
        exit()
    words = input("Which words do you want to see comparisons of? (Multiple words separated by whitespace) => ")
    wordlist = words.split() # get individual words
    word_vectors = dict()
    word_facts = dict()
    # data = pd.read_csv("data.csv",sep = "\t") # ,converters = {"Word Vector": torch.Tensor, "Sentence Vector": torch.Tensor}) # get dataframe from file
    data = data.dropna(subset=['Word Vector', 'Sentence Vector']) # remove all rows that contain nan in word vector or sentence vector
    data = data.reset_index(drop=True)
    # torch.tensor(data['Word Vector'].values, dtype = torch.float32)
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
                    # print(word)
                    # wordlist.remove(word)
                    break
                else:
                    answer = input("Invalid input. Please only type 'Y' or 'N': => ")
        else:
            # count entries in data (one entry = one sense)
            visited = []
            # senses = 0
            for i in range(0, len(data['Word'])):
                if word == data["Word"][i]:
                    visited.append(i) # store the index of this entry
                    # print(data["Word"][i], data["Sense"][i])
                    # senses += 1
                    continue
            print(str(len(visited)) + " entries found for " + word)

            for index in visited:
                # word_vector = torch.as_tensor(data["Word Vector"][index],dtype = torch.float)
                # print(data["Word Vector"][index])
                word_vector = data["Word Vector"][index].tolist()
                number = ["number: " + data["Number"][index]]
                example = ["example: " + data["Sentence"][index]]
                if index not in word_facts.keys():
                    word_facts[(word,data["Sense"][index])] = [number,example] # store facts for later
                # print(word_vector)
                # print(word_vector.tolist())
                # exit()
                # if (word,data["Sense"][index]) not in word_vectors.keys():
                word_vectors[(word,data["Sense"][index])] = word_vector
if len(word_vectors.keys()) != 0:
    # print(word_vectors.keys())
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