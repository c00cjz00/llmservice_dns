import os
import sys
import urllib.request
import urllib.parse
import urllib.error
import zipfile

import xml.parsers.expat
import html2text
from glob import glob


class ContainerParser():
    def __init__(self, xmlcontent=None):
        self.rootfile = ""
        self.xml = xmlcontent

    def startElement(self, name, attributes):
        if name == "rootfile":
            self.buffer = ""
            self.rootfile = attributes["full-path"]

    def parseContainer(self):
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.startElement
        parser.Parse(self.xml, 1)
        return self.rootfile


class BookParser():
    def __init__(self, xmlcontent=None):
        self.xml = xmlcontent
        self.title = ""
        self.author = ""
        self.inTitle = 0
        self.inAuthor = 0
        self.ncx = ""

    def startElement(self, name, attributes):
        if name == "dc:title":
            self.buffer = ""
            self.inTitle = 1
        elif name == "dc:creator":
            self.buffer = ""
            self.inAuthor = 1
        elif name == "item":
            if attributes["id"] == "ncx" or attributes["id"] == "toc" or attributes["id"] == "ncxtoc":
                self.ncx = attributes["href"]

    def characters(self, data):
        if self.inTitle:
            self.buffer += data
        elif self.inAuthor:
            self.buffer += data

    def endElement(self, name):
        if name == "dc:title":
            self.inTitle = 0
            self.title = self.buffer
            self.buffer = ""
        elif name == "dc:creator":
            self.inAuthor = 0
            self.author = self.buffer
            self.buffer = ""

    def parseBook(self):
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characters
        parser.Parse(self.xml, 1)
        return self.title, self.author, self.ncx


class NavPoint():
    def __init__(self, id=None, playorder=None, level=0, content=None, text=None):
        self.id = id
        self.content = content
        self.playorder = playorder
        self.level = level
        self.text = text


class TocParser():
    def __init__(self, xmlcontent=None):
        self.xml = xmlcontent
        self.currentNP = None
        self.stack = []
        self.inText = 0
        self.toc = []

    def startElement(self, name, attributes):
        if name == "navPoint":
            level = len(self.stack)
            self.currentNP = NavPoint(
                attributes["id"], attributes.get("playOrder", ""), level)
            self.stack.append(self.currentNP)
            self.toc.append(self.currentNP)
        elif name == "content":
            self.currentNP.content = urllib.parse.unquote(attributes["src"])
        elif name == "text":
            self.buffer = ""
            self.inText = 1

    def characters(self, data):
        if self.inText:
            self.buffer += data

    def endElement(self, name):
        if name == "navPoint":
            self.currentNP = self.stack.pop()
        elif name == "text":
            if self.inText and self.currentNP:
                self.currentNP.text = self.buffer
            self.inText = 0

    def parseToc(self):
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characters
        parser.Parse(self.xml, 1)
        return self.toc



def convert(epub):
    try:
        file = zipfile.ZipFile(epub, "r")
        result = []
        rootfile = ContainerParser(
            file.read("META-INF/container.xml")).parseContainer()
        title, author, ncx = BookParser(file.read(rootfile)).parseBook()
        # result.append(f'{title.strip()} 作者: {author.strip()}')
        ops = "/".join(rootfile.split("/")[:-1])
        if ops != "":
            ops = ops+"/"
        toc = TocParser(file.read(ops + ncx)).parseToc()

        for t in toc:
            html = file.read(ops + t.content.split("#")[0])
            text = html2text.html2text(html.decode("utf-8"))
            text = text.replace("  \n  \n", "\n")
            result.append(text.strip())
        file.close()
        # except Exception as e:
        #     print(f"Error loading {epub}: {e}")
        #     return ''
    except Exception as e:
        print(f"Error loading {epub}: {e}")
        return ''
    
    return '\n\n'.join(result)


# 直式括號轉橫式括號
def r2c(dct: dict):
    PUNCT = {
        '﹂': '」',
        '﹁': '「',
        '︵': '（',
        '︶': '）',
        '｜｜': '',
        '︻': '【',
        '︼': '】',
    }
    for k, v in PUNCT.items():
        dct['text'] = dct['text'].replace(k, v)
    return dct


def usage():
    print("Usage: epub2txt <path-to-epub>")


if __name__ == "__main__":
    import glob
    from datasets import Dataset
    from tqdm import tqdm
    from concurrent.futures import ProcessPoolExecutor
    
    if (len(sys.argv) == 1 or sys.argv[1] == "help"):
        usage()
    
    elif sys.argv[1]:
        result = []
        filenames = glob.glob(f'{sys.argv[1]}/**/*.epub', recursive=True)
        filenames += glob.glob(f'{sys.argv[1]}/*.epub', recursive=True)
        filenames = list(set(filenames))
        with ProcessPoolExecutor(16) as executor:
            result = list(tqdm(executor.map(convert, filenames)))
        ds = Dataset.from_dict({'text': result})
        ds = ds.filter(lambda x: len(x['text']) > 10, num_proc=16)
        ds = ds.map(r2c, num_proc=16)
        ds.to_json(sys.argv[2], lines=True, force_ascii=False)