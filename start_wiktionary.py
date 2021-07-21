import sys
# from tqdm import tqdm
import time
import os

languages = ["english","german","spanish"]

if sys.argv[1]:
    language = sys.argv[1].lower()
    if language not in languages:
        print(language + " is not supported")
        sys.exit()
    languages.remove(language)
else:
    print("Missing argument: <language>")
    sys.exit()
shorts = {"english":"en","german":"de","spanish":"es"}
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
parser = {"english":english_xml_parser,"german":german_xml_parser,"spanish":spanish_xml_parser}
if win:
    path = language + "_wiktionary\\wiktionaries\\"
else:
    path = language + "_wiktionary/wiktionaries/"
with open(path + shorts[language] + "wiktionary-new.txt",mode="w+",encoding="utf-8") as wiktionary_out:
    n=1 # entry counter
    print("Processing data from " + language + " wiktionary...")
    # use individually splitted files
    if win:
#         for filename in tqdm(os.listdir(path + "by_entry\\")): # \ for Windows, / for Linux
        for filename in os.listdir(path + "by_entry\\"):
            with open(path + "by_entry\\" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                parser[language](language,shorts,file_in_wiktionary,wiktionary_out)
    else:
        for filename in os.listdir(path + "by_entry/"):
#         for filename in tqdm(os.listdir(path + "by_entry/")): # \ for Windows, / for Linux
            with open(path + "by_entry/" + filename, mode = "r", encoding = "utf-8") as file_in_wiktionary:
                parser[language](language,shorts,file_in_wiktionary,wiktionary_out)
    for other in languages:
        print("Processing data from " + other + " wiktionary...")
        with open(language + "_from_" + other + "_dump.xml",mode="r",encoding="utf-8") as other_file:
            parser[other](language,shorts,other_file,wiktionary_out)
end = time.time()
print(str(end-start)," seconds")
