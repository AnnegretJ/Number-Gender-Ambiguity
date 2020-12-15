import xml.etree.ElementTree as ET
import re
import os
import sys
import time

# path = "C:\\Users\\Tili\\Documents\\DFKI\\MLT\\BERT-stuff\\wiktionary\\wiktionaries\\"

start = time.time()
if len(sys.argv) >= 2:
    if sys.argv[1] in ["German","English","Spanish"]:
        language = sys.argv[1]
        if len(sys.argv) >= 3:
            path = ""
            original = sys.argv[2]
        else:
            if language == "German":
                try:
                    if "linux" in sys.platform:
                        path = "german_wiktionary/wiktionaries/"
                    elif "win" in sys.platform:
                        path = "german_wiktionary\\wiktionaries\\"
                    else:
                        print("Not available for ", sys.platform)
                        sys.exit()
                    original = path + "dewiktionary-20200501-pages-articles.xml"
                except FileNotFoundError:
                    print("Please specify a path.")
                    sys.exit()
            elif language == "English":
                try:
                    if "linux" in sys.platform:
                        path = "english_wiktionary/wiktionaries/"
                    elif "win" in sys.platform:
                        path = "english_wiktionary\\wiktionaries\\"
                    else:
                        print("Not available for ", sys.platform)
                        sys.exit()
                    original = path + "enwiktionary-20200501-pages-articles.xml"
                except FileNotFoundError:
                    print("Please specify a path.")
                    sys.exit()
            elif language == "Spanish":
                try:
                    if "linux" in sys.platform:
                        path + "spanish_wiktionary/wiktionaries/"
                    elif "win" in sys.platform:
                        path = "spanish_wiktionary\\wiktionaries\\"
                    else:
                        print("Not available for ", sys.platform)
                        sys.exit()
                    original = path + "eswiktionary-20200501-pages-articles.xml"
                except FileNotFoundError:
                    print("Please specify a path.")
                    sys.exit()
    else:
        print(sys.argv[1], " is not available. Please choose from <German, English, Spanish>.")
        sys.exit()
else:
    print("No language has been specified. Please choose from <German, English, Spanish>.")
    sys.exit()

# original = path + "enwiktionary-20200501-short.xml"

if "win" in sys.platform:
    win = True
else:
    win = False
n = 1
if language == "German":
    child_language_pattern = re.compile(r"\(\{\{Sprache\|(.*?)\}\}\)")
    # ({{Sprache|Latein}}) ==
    context = ET.iterparse(original, events=('end', ))
    with open("spanish_from_german_dump.xml","wb") as s:
        s.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="de">\n')
        with open("english_from_german_dump.xml","wb") as e:
            e.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="de">\n')
            try:
                while True:
                    if path != "german_wiktionary\\wiktionaries\\" and path != "german_wiktionary/wiktionaries/":
                        try:
                            if win:
                                os.mkdir("german_wiktionary\\wiktionaries")
                                path = "german_wiktionary\\wiktionaries\\"
                            else:
                                os.mkdir("german_wiktionary/wiktionaries")
                                path = "german_wiktionary/wiktionaries/"
                        except FileExistsError:
                            if win:
                                path = "german_wiktionary\\wiktionaries\\"
                            else:
                                path = "german_wiktionary/wiktionaries/"
                    try:
                        if win:
                            os.mkdir("german_wiktionary\\wiktionaries\\by_entry\\")
                            title = path + "by_entry\\dewiktionary_short_" + str(n)
                        else:
                            os.mkdir("german_wiktionary/wiktionaries/by_entry/")
                            title = path + "by_entry/dewiktionary_short_" + str(n)
                    except FileExistsError:
                        if win:
                            title = path + "by_entry\\dewiktionary_short_" + str(n)
                        else:
                            title = path + "by_entry/dewiktionary_short_" + str(n)
                    filename = title + ".xml"
                    with open(filename, 'wb') as f:
                        f.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="de">\n')
                        for _ in range(50000):
                            event, elem = next(context)
                            if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                                for child in elem.iter():
                                    if child.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
                                        for grandchild in child.iter():
                                            if grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}text" and grandchild.text != None:
                                                if child_language_pattern.search(grandchild.text):
                                                    if child_language_pattern.search(grandchild.text).group(1) == "Englisch":
                                                        e.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                                        elem.clear()
                                                        break
                                                    elif child_language_pattern.search(grandchild.text).group(1) == "Spanisch":
                                                        s.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                                        elem.clear()
                                                        break
                                    elif child.tag == "{http://www.mediawiki.org/xml/export-0.10/}title" and ":" in child.text:
                                        child.clear()
                                        break
                                f.write(b"<page>\n" + ET.tostring(elem) + b"</page>\n")
                                elem.clear()
                        f.write(b'</mediawiki>')
                    n+=1
            except StopIteration:
                with open(filename, "ab") as f:
                    f.write(b'</mediawiki>')
            print(str(n) + " new files")
            e.write(b"</mediawiki>")
        s.write(b"</mediawiki>")
elif language == "English":
    child_language_pattern = re.compile(r"\}\}\n==(.*?)==")
    context = ET.iterparse(original, events=("end", ))
    with open("spanish_from_english_dump.xml","wb") as s:
        s.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="de">\n')
        with open("german_from_english_dump.xml","wb") as g:
            g.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="de">\n')
            try:
                while True:
                    if path != "english_wiktionary\\wiktionaries\\" and path != "english_wiktionary/wiktionaries/":
                        try:
                            if win:
                                os.mkdir("english_wiktionary\\wiktionaries\\")
                                path = "english_wiktionary\\wiktionaries\\"
                            else:
                                os.mkdir("english_wiktionary/wiktionaries")
                                path = "english_wiktionary/wiktionaries/"
                        except FileExistsError:
                            if win:
                                path = "english_wiktionary\\wiktionaries\\"
                            else:
                                path = "english_wiktionary/wiktionaries/"
                    try:
                        if win:
                            os.mkdir("english_wiktionary\\wiktionaries\\by_entry\\")
                            title = path + "by_entry\\enwiktionary_short_" + str(n)
                        else:
                            os.mkdir("english_wiktionary/wiktionaries/by_entry")
                            title = path + "by_entry/enwiktionary_short_" + str(n)
                    except FileExistsError:
                        if win:
                            new = "by_entry\\enwiktionary_short_"
                            title = path + new + str(n)
                        else:
                            new = "by_entry/enwiktionary_short_"
                            title = path + new + str(n)
                    filename = title + ".xml"
                    with open(filename, 'wb') as f:
                        f.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="en">\n')
                        for _ in range(50000):
                            event, elem = next(context)
                            if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                                for child in elem:
                                    if child.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
                                        for grandchild in child:
                                            if grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}text" and grandchild.text != None:
                                                if child_language_pattern.search(grandchild.text):
                                                    if child_language_pattern.search(grandchild.text).group(1) != language:
                                                        if child_language_pattern.search(grandchild.text).group(1) == "Spanish":
                                                            s.write( b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                                            elem.clear()
                                                            break
                                                        elif child_language_pattern.search(grandchild.text).group(1) == "German":
                                                            g.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                                            elem.clear()
                                                            break
                                                        else:
                                                            child.clear()
                                    elif child.tag == "{http://www.mediawiki.org/xml/export-0.10/}title" and ":" in child.text:
                                        child.clear()
                                        break
                                f.write(b"<page>\n" + ET.tostring(elem) + b"</page>\n")
                                elem.clear()
                        f.write(b'</mediawiki>')
                    n+=1     
            except StopIteration:
                with open(filename, "ab") as f:
                    f.write(b'</mediawiki>')
            print(str(n) + " new files")
            g.write(b"</mediawiki>")
        s.write(b"</mediawiki>")
elif language == "Spanish":
    child_language_pattern = re.compile(r"== \{\{lengua\|(.*?)\}\} ==")
    context = ET.iterparse(original, events=('end', ))
    with open("german_from_spanish_dump.xml","wb") as g:
        g.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="es">\n')
        with open("english_from_spanish_dump.xml","wb") as e:
            e.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="es">\n')
            try:
                while True:
                    if path != "spanish_wiktionary\\wiktionaries\\" and path != "spanish_wiktionary/wiktionaries/":
                        try:
                            if win:
                                os.mkdir("spanish_wiktionary\\wiktionaries\\")
                                path = "spanish_wiktionary\\wiktionaries\\"
                            else:
                                os.mkdir("spanish_wiktionary/wiktionaries/")
                                path = "spanish_wiktionary/wiktionaries/"
                        except FileExistsError:
                            if win:
                                path = "spanish_wiktionary\\wiktionaries\\"
                            else:
                                path = "spanish_wiktionary/wiktionaries/"
                    try:
                        if win:
                            os.mkdir("spanish_wiktionary\\wiktionaries\\by_entry\\")
                            title = path + "by_entry\\eswiktionary_short_" + str(n)
                        else:
                            os.mkdir("spanish_wiktionary/wiktionaries/by_entry/")
                            title = path + "by_entry/eswiktionary_short_" + str(n)
                    except FileExistsError:
                        if win:
                            title = path + "by_entry\\eswiktionary_short_" + str(n)
                        else:
                            title = path + "by_entry/eswiktionary_short_" + str(n)
                    filename = title + ".xml"
                    with open(filename, 'wb') as f:
                        f.write(b'<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="es">\n')
                        for _ in range(50000):
                            event, elem = next(context)
                            if elem.tag == '{http://www.mediawiki.org/xml/export-0.10/}page':
                                for child in elem.iter():
                                    if child.tag == "{http://www.mediawiki.org/xml/export-0.10/}revision":
                                        for grandchild in child.iter():
                                            if grandchild.tag == "{http://www.mediawiki.org/xml/export-0.10/}text" and grandchild.text != None:
                                                if child_language_pattern.search(grandchild.text):
                                                    if child_language_pattern.search(grandchild.text).group(1) == "en":
                                                        e.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                                        elem.clear()
                                                        break
                                                    elif child_language_pattern.search(grandchild.text).group(1) == "de":
                                                        g.write(b"\n<page>\n" + ET.tostring(elem) + b"</page>\n")
                                                        elem.clear()
                                                        break
                                    elif child.tag == "{http://www.mediawiki.org/xml/export-0.10/}title" and ":" in child.text:
                                        child.clear()
                                        break
                                f.write(b"<page>\n" + ET.tostring(elem) + b"</page>\n")
                                elem.clear()
                        f.write(b'</mediawiki>')
                    n+=1
            except StopIteration:
                with open(filename, "ab") as f:
                    f.write(b'</mediawiki>')
            print(str(n) + " new files")
            e.write(b"</mediawiki>")
        g.write(b"</mediawiki>")
end = time.time()
print(str(end-start)+ " seconds")