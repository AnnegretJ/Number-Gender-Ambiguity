import sys
from tqdm import tqdm

import os
sys.path.insert(1, "spanish_wiktionary\\")
from es_wiktionary import spanish_xml_parser
sys.path.insert(1, "english_wiktionary\\")
from en_wiktionary import english_xml_parser
sys.path.insert(1, "german_wiktionary\\")
from de_wiktionary import german_xml_parser

if sys.argv[1]:
    language = sys.argv[1]
    if language.lower() == "english":
        path = "english_wiktionary\\wiktionaries\\"
        with open(path +'enwiktionary-new.txt', mode='w+', encoding="utf8") as wiktionary_out:
            n=1 # entry counter
            print("Processing data from English wiktionary...")
            for filename in tqdm(os.listdir(path + "by_entry\\")): # \ for Windows, / for Linux
                with open(path + "by_entry\\" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                    english_xml_parser(language,file_in_wiktionary,wiktionary_out,)
            print("Processing data from German wiktionary...")
            with open("english_from_german_dump.xml",mode="r",encoding="utf-8") as g:
                german_xml_parser(language,g,wiktionary_out,entries=dict(),n=n)
            print("Processing data from Spanish wiktionary...")
            with open("english_from_spanish_dump.xml",mode="r",encoding="utf-8") as s:
                spanish_xml_parser(language,s,wiktionary_out,n)
    elif language.lower() == "german":
        # path to data
        path = "german_wiktionary\\wiktionaries\\"
        entries = dict()
        possible_regular_plurals = set()
        with open(path + "dewiktionary-new.txt", mode = "w+", encoding = "utf-8") as wiktionary_out:
            n=1
            print("Processing data from German wiktionary...")
            for filename in tqdm(os.listdir(path + "by_entry/")):
                with open(path + "by_entry/" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                    german_xml_parser("German",file_in_wiktionary,wiktionary_out,entries=entries,plurals=possible_regular_plurals,n=n)
            print("Processing data from English wiktionary...")
            with open("german_from_english_dump.xml",mode="r",encoding="utf-8") as e:
                english_xml_parser(language,e,wiktionary_out,n=n)
            print("Processing data from Spanish wiktionary...")
            with open("german_from_spanish_dump.xml",mode="r",encoding="utf-8") as s:
                spanish_xml_parser(language,s,wiktionary_out,n=n)
    elif language.lower() == "spanish":
        # path to data
        path = "spanish_wiktionary\\wiktionaries\\"
        with open(path +'eswiktionary-new.txt', mode='w+', encoding="utf8") as wiktionary_out:
            n = 1
            print("Processing data from Spanish wiktionary...")
            for filename in tqdm(os.listdir(path + "by_entry\\")): # \ for Windows, / for Linux
                with open(path + "by_entry\\" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                    spanish_xml_parser("Spanish",file_in_wiktionary,wiktionary_out,n)     
            print("Processing data from English wiktionary...")
            with open("spanish_from_english_dump.xml",encoding="utf-8") as e:
                english_xml_parser(language,e,wiktionary_out,n=n)
            print("Processing data from German wiktionary...")
            with open("spanish_from_german_dump.xml",encoding="utf-8") as g:
                german_xml_parser(language,g,wiktionary_out,entries=dict(),n=n)
    else:
        print("Invalid argument.")
        sys.exit()
else:
    print("Missing argument: <language>")
    sys.exit()