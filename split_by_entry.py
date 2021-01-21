import xml.etree.ElementTree as ET
import re
import os
import sys
import time

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
                if language == "german":
                    original = path + "dewiktionary-20200501-pages-articles.xml"
                    short = "de"
                    mediawiki = b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="de">\n'
                    child_language_pattern = re.compile(r"\(\{\{Sprache\|(.*?)\}\}\)")
                elif language == "english":
                    original = path + "enwiktionary-20200501-pages-articles.xml"
                    short = "en"
                    mediawiki = b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="en">\n'
                    child_language_pattern = re.compile(r"\}\}\n==(.*?)==")
                elif language == "spanish":
                    original = path + "eswiktionary-20200501-pages-articles.xml"
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