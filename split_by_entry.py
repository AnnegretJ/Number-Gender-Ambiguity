import xml.etree.ElementTree as ET
import re
import os
import sys
import time
from os.path import exists
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import bz2
from bz2 import decompress
import shutil
from datetime import date

def get_wiktionary_data(language,path):
    # initialize general urls for wiktionary dumps
    if language == "english":
        url = "https://dumps.wikimedia.org/enwiktionary/"
        wiki = "enwiktionary"
    elif language == "german":
        url = "https://dumps.wikimedia.org/dewiktionary/"
        wiki = "dewiktionary"
    elif language == "spanish":
        url = "https://dumps.wikimedia.org/eswiktionary/"
        wiki = "eswiktionary"
    else:
        print(language + " is not supported")
        sys.exit()
    def is_valid(url):
        '''
        Checks if the given url is valid\n
        ;param url: some URL
        '''
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    if not is_valid(url):
        print(url, "is not a vaild URL")
        sys.exit()
    name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content,"html.parser") # get urls
    for a_tag in soup.findAll("a"):
        new = a_tag.attrs.get("href")
        if new == "" or new is None:
            continue
        if "latest" in new: # the url before "latest" is the newest relevant one
            break
        href = new # save as "previous"
    new_url = urljoin(url,href) # get the url of the newest dump
    number = href.strip("/")
    filename = wiki + "-" + number + "-pages-articles.xml.bz2"
    xml_filename = wiki + "-" + number + "-pages-articles.xml"
    if not is_valid(new_url):
        print(new_url, " is not a valid URL")
        sys.exit()
    if not exists(path + filename):
        data_url = urljoin(new_url, filename).replace("\\","/")
        if not is_valid(data_url):
            print(data_url, " is not a valid URL")
            sys.exit()
        datafile = requests.get(data_url) # download data
        print("Data downloaded successfully")
        with open("url_data.xml.bz2", "wb") as f:
            f.write(datafile.content)
        # decompress file
        print("Decompress data...")
        decompressor = bz2.BZ2Decompressor()
        with open(path+xml_filename, 'wb') as new_file, open("url_data.xml.bz2", 'rb') as file:
            for data in iter(lambda : file.read(100 * 1024), b''):
                new_file.write(decompressor.decompress(data))
    return path + xml_filename

start = time.time()
languages = ["german","english","spanish"]
if len(sys.argv) >= 2:
    if sys.argv[1].lower() in languages:
        language = sys.argv[1].lower()
        if len(sys.argv) >= 3:
            path = ""
            original = sys.argv[2]
        else:
            try:
                if "linux" in sys.platform:
                    path = language + "_wiktionary/wiktionaries/"
                    win = False
                elif "win" in sys.platform:
                    path = language + "_wiktionary\\wiktionaries\\"
                    win = True
                else:
                    print("Not available for ", sys.platform)
                    sys.exit()
                print("Getting data...")
                current_day = date.today().strftime("%d")
                if int(current_day) >= 20:
                    current_date = date.today().strftime("%Y" + "%m" + "20")
                else:
                    current_date = date.today().strftime("%Y" + str(int("%m")-1) + "20")
                try:
                    if language == "english":
                        wiktionary = "enwiktionary"
                    elif language == "german":
                        wiktionary = "dewiktionary"
                    elif language == "spanish":
                        wiktionary = "eswiktionary"
                    original = path + wiktionary + "-" + current_date + "-pages-articles.xml"
                except FileNotFoundError:
                    try:
                        os.mkdir(path+"backup_data/")
                    except FileExistsError:
                        pass
                    for file in os.listdir(path):
                        if file.endswith(".xml"):
                           shutil.move(path+file,path+"backup_data/")
                    original = get_wiktionary_data(language,path)
                if language == "german":
                    short = "de"
                    mediawiki = b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="de">\n'
                    child_language_pattern = re.compile(r"\(\{\{Sprache\|(.*?)\}\}\)")
                elif language == "english":
                    short = "en"
                    mediawiki = b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="en">\n'
                    child_language_pattern = re.compile(r"\}\}\n==(.*?)==")
                elif language == "spanish":
                    short = "es"
                    mediawiki = b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="es">\n'
                    child_language_pattern = re.compile(r"== \{\{lengua\|(.*?)\}\} ==")
            except FileNotFoundError:
                print("Please specify a path.")
                sys.exit()
    else:
        print(sys.argv[1], " is not available. Please choose from <German, English, Spanish>.")
        sys.exit()
else:
    print("No language has been specified. Please choose from <German, English, Spanish>.")
    sys.exit()

n = 1
context = ET.iterparse(original, events=('end', ))
for i in range(len(languages)):
    if languages[i] == language:
        del languages[i]
        break
first = open(languages[0] + "_from_" + language + "_dump.xml","wb")
first.write(mediawiki)
second = open(languages[1] + "_from_" + language + "_dump.xml","wb")
second.write(mediawiki)
try:
    while True:
        if path != language + "_wiktionary\\wiktionaries\\" and path != language + "_wiktionary/wiktionaries/":
            try:
                if win:
                    os.mkdir(language + "_wiktionary\\wiktionaries")
                    path = language + "_wiktionary\\wiktionaries\\"
                else:
                    os.mkdir(language + "_wiktionary/wiktionaries")
                    path = language + "_wiktionary/wiktionaries/"
            except FileExistsError:
                if win:
                    path = language + "_wiktionary\\wiktionaries\\"
                else:
                    path = language + "_wiktionary/wiktionaries/"
        try:
            if win:
                os.mkdir(language + "_wiktionary\\wiktionaries\\by_entry\\")
                title = path + "by_entry\\" + short + "wiktionary_short_" + str(n)
            else:
                os.mkdir(language + "_wiktionary/wiktionaries/by_entry/")
                title = path + "by_entry/" + short + "wiktionary_short_" + str(n)
        except FileExistsError:
            if win:
                title = path + "by_entry\\" + short + "wiktionary_short_" + str(n)
            else:
                title = path + "by_entry/" + short + "wiktionary_short_" + str(n)
        filename = title + ".xml"
        with open(filename, 'wb') as f:
            f.write(mediawiki)
            i = 0
            while i in range(20000):
                event, elem = next(context)
                if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                    for child in elem.iter():
                        if child.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
                            for grandchild in child.iter():
                                if grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}text" and grandchild.text != None:
                                    if child_language_pattern.search(grandchild.text):
                                        other = child_language_pattern.search(grandchild.text).group(1)
                                        # sort into according files for other languages
                                        # does not do anything with entries of current language, as this language is not in languages anymore
                                        if other == "Englisch" or other == "en":
                                            if languages[0] == "english":
                                                first.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                            elif languages[1] == "english":
                                                second.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                            elem.clear()
                                            break
                                        elif other == "Spanisch" or other == "Spanish":
                                            if languages[0] == "spanish":
                                                first.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                            elif languages[1] == "spanish":
                                                second.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                            elem.clear()
                                            break
                                        elif other == "German" or other == "de":
                                            if languages[0] == "german":
                                                first.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                            elif languages[1] == "german":
                                                second.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                            elem.clear()
                                            break
                                        else:
                                            break # skip other languages
                        elif child.tag == "{http://www.mediawiki.org/xml/export-0.10/}title" and ":" in child.text:
                            child.clear()
                            break
                    f.write(b"<page>\n" + ET.tostring(elem) + b"</page>\n")
                    i += 1
                    elem.clear()
            f.write(b'</mediawiki>')
            print(n)
        n+=1
except StopIteration:
    with open(filename, "ab") as f:
        f.write(b'</mediawiki>')
print(str(n) + " new files")
first.write(b"</mediawiki>")
first.close()
second.write(b"</mediawiki>")
second.close()
end = time.time()
print(str(end-start)+ " seconds")
