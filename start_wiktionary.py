import sys
from tqdm import tqdm
import time

import os
# get pathways to all necessary files
if "win" in sys.platform:
    win = True
    sys.path.insert(1, "spanish_wiktionary\\")
    from es_wiktionary import spanish_xml_parser
    sys.path.insert(1, "english_wiktionary\\")
    from en_wiktionary import english_xml_parser
    sys.path.insert(1, "german_wiktionary\\")
    from de_wiktionary import german_xml_parser
elif "linux" in sys.platform:
    win = False
    sys.path.insert(1, "spanish_wiktionary/")
    from es_wiktionary import spanish_xml_parser
    sys.path.insert(1, "english_wiktionary/")
    from en_wiktionary import english_xml_parser
    sys.path.insert(1, "german_wiktionary/")
    from de_wiktionary import german_xml_parser
else:
    print(sys.platform, " is not supported.")

start = time.time()
if sys.argv[1]:
    language = sys.argv[1]
    # process English files
    if language.lower() == "english":
        if win:
            path = "english_wiktionary\\wiktionaries\\"
        else:
            path = "english_wiktionary/wiktionaries/"
        with open(path +'enwiktionary-new.txt', mode='w+', encoding="utf8") as wiktionary_out:
            n=1 # entry counter
            print("Processing data from English wiktionary...")
            # use individually splitted files
            if win:
                for filename in tqdm(os.listdir(path + "by_entry\\")): # \ for Windows, / for Linux
                    with open(path + "by_entry\\" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                        english_xml_parser("English",file_in_wiktionary,wiktionary_out)
            else:
                for filename in tqdm(os.listdir(path + "by_entry/")): # \ for Windows, / for Linux
                    with open(path + "by_entry/" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                        english_xml_parser("English",file_in_wiktionary,wiktionary_out)
            # use English data found in the German dump
            print("Processing data from German wiktionary...")
            with open("english_from_german_dump.xml",mode="r",encoding="utf-8") as g:
                german_xml_parser("English",g,wiktionary_out,entries=dict(),n=n)
            # use English data found in the Spanish dump
            print("Processing data from Spanish wiktionary...")
            with open("english_from_spanish_dump.xml",mode="r",encoding="utf-8") as s:
                spanish_xml_parser("English",s,wiktionary_out)
    # process German files
    elif language.lower() == "german":
        # path to data
        if win:
            path = "german_wiktionary\\wiktionaries\\"
        else:
            path = "german_wiktionary/wiktionaries/"
        entries = dict()
        possible_regular_plurals = set()
        with open(path + "dewiktionary-new.txt", mode = "w+", encoding = "utf-8") as wiktionary_out:
            n=1
            print("Processing data from German wiktionary...")
            # use individually splitted files
            if win:
                for filename in tqdm(os.listdir(path + "by_entry\\")):
                    with open(path + "by_entry\\" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                        german_xml_parser("German",file_in_wiktionary,wiktionary_out,entries=entries,plurals=possible_regular_plurals,n=n)
            else:
                for filename in tqdm(os.listdir(path + "by_entry/")):
                    with open(path + "by_entry/" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                        german_xml_parser("German",file_in_wiktionary,wiktionary_out,entries=entries,plurals=possible_regular_plurals,n=n)
            # use German data found in the English dump
            print("Processing data from English wiktionary...")
            with open("german_from_english_dump.xml",mode="r",encoding="utf-8") as e:
                english_xml_parser(language,e,wiktionary_out)
            # use German data found in the Spanish dump
            print("Processing data from Spanish wiktionary...")
            with open("german_from_spanish_dump.xml",mode="r",encoding="utf-8") as s:
                spanish_xml_parser(language,s,wiktionary_out)
    # process Spanish files
    elif language.lower() == "spanish":
        # path to data
        if win:
            path = "spanish_wiktionary\\wiktionaries\\"
        else:
            path = "spanish_wiktionary/wiktionaries/"
        with open(path +'eswiktionary-new.txt', mode='w+', encoding="utf8") as wiktionary_out:
            n = 1
            print("Processing data from Spanish wiktionary...")
            # use individually splitted files
            if win:
                for filename in tqdm(os.listdir(path + "by_entry\\")): # \ for Windows, / for Linux
                    with open(path + "by_entry\\" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                        spanish_xml_parser("Spanish",file_in_wiktionary,wiktionary_out)
            else:
                for filename in tqdm(os.listdir(path + "by_entry/")): # \ for Windows, / for Linux
                    with open(path + "by_entry/" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                        spanish_xml_parser("Spanish",file_in_wiktionary,wiktionary_out)
            # use Spanish data found in the English dump
            print("Processing data from English wiktionary...")
            with open("spanish_from_english_dump.xml",encoding="utf-8") as e:
                english_xml_parser("Spanish",e,wiktionary_out)
            # use Spanish data found in the German dump
            print("Processing data from German wiktionary...")
            with open("spanish_from_german_dump.xml",encoding="utf-8") as g:
                german_xml_parser("Spanish",g,wiktionary_out,entries=dict(),n=n)
    else:
        print("Invalid argument.")
        sys.exit()
else:
    print("Missing argument: <language>")
    sys.exit()
end = time.time()
print(str(end-start)," seconds")