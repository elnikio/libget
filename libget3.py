#!/usr/bin/python3.7

from urllib.request import urlopen
from uritools import urijoin
from bs4 import BeautifulSoup
import wget
import shutil
import wget
import shutil
import os
import re
import sys

def print_contents(content_list):
    index = 0
    for content in content_list:
        print(f"contents[%d] = %s" % (index, content))
        index += 1
    return 0

def splitAtIndex(string, index):
    output = []
    for i in range(0, index):
        output.append(string[i])
    string = output
    return string

"""
To-do:
    - implemment search by name
    - implement options list
    - implement partial downloads (may have to replace wget() with request())
"""

keywords = [
    "-h",
    "-j",
    "-a",
    "-o",
    "-b",
    "-c",
    "-m",
    "-f",
    "-s",
    "--ext-pref",
    "--get-ret",
    "--down-lim",
    "--time-lim",
    "--vol-start",
    "--vol-end",
    "-vs",
    "-ve"
]

options = {
    "-h": "help: print all commands",
    "-j": "journal name(s)",
    "-a": "article name(s)",
    "-o": "output dir(s)",
    "-b": "book name(s)",
    "-c": "comic name(s)",
    "-m": "magazine name(s)",
    "-f": "fiction name(s)",
    "-s": "standard name(s)",
    "--ext-pref": "list of file extensions, ordered by preference",
    "--get-ret": "maximum number of wget retries",
    "--down-lim": "limit of total download size",
    "--time-lim": "time limit of full operation",
    "--vol-start / -vs": "starting volumme",
    "--vol-end / -ve": "ending volume"
}

requests = {
    "journals": 0,
    "books": 0,
    "comics": 0,
    "articles": 0,
    "outputs": 0
}

journals = []
outputs = []

volEnd = None
volStart = None
parsingJournals = False
parsingOutputs = False

for arg in sys.argv:
    if arg == "-j":
        parsingJournals = True
        parsingOutputs = False
        print("----------------\nPARSING JOURNALS")
        continue
    if arg == "-o":
        print("----------------\nPARSING  OUTPUTS")
        parsingOutputs = True
        parsingJournals = False
        continue
    if arg == "-vs" or arg == "--vol-start":
        volStart = int(sys.argv[sys.argv.index(arg) + 1])
        continue
    if arg == "-ve" or arg == "--vol-end":
        volEnd = int(sys.argv[sys.argv.index(arg) + 1])
        continue
    if arg in keywords:
        parsingJournals = False
        parsingOutputs = False
        print("----------------")
        continue
    if parsingJournals:
        print("parsing journal", arg+"...")
        journals.append(arg)
        requests["journals"] += 1
        continue
    if parsingOutputs:
        print("parsing output", arg+"...")
        outputs.append(arg)
        requests["outputs"] += 1

requestsSum = requests["journals"] + requests["books"] + requests["comics"] + requests["articles"]

for i in range(0, len(journals)):
    # AUTO OUTPUT DIR
    if outputs[i] == "auto":
        outputs[i] = "/media/nikola/h/My Journals/"+journals[i]+"/"
    print(journals[i], ":", outputs[i])

if requestsSum > requests["outputs"]:
    print("Error: Not enough output targets provided.")
    exit()

if requestsSum < requests["outputs"]:
    print("Error: Too many output targets provided.")
    exit()

for i in range(0, len(journals)):
    journals[i] = journals[i].lower()
    fLet = (journals[i][0]).upper()
    html = urlopen("https://libgen.is/scimag/journals/?letter=other")
    bs = BeautifulSoup(html.read(), "html.parser")
    url = urijoin('http://libgen.is', bs.find(href=re.compile(f"(letter={fLet})"))['href'])
    html = urlopen(url)
    bs = BeautifulSoup(html.read(), "html.parser")

    found = False
    for jurRef in bs.findAll(href=re.compile("(/scimag/journals/\d)")):
        if jurRef.string.lower() == journals[i]:
            journal_URL = urijoin("http://libgen.is", jurRef['href'])
            print("Journal", journals[i], "found at", jurRef['href'])
            found = True

    if found == False:
        print("Journal", journals[i], "not found. Skipping...")
        continue

    #mirror = "Sci-Hub"
    mirror = "Libgen"

    # SET JOURNAL DIRECTORY
    if outputs[i].endswith('/') == False:
        outputs[i] = outputs[i] + '/'
    print("Downloading", journals[i], "to", outputs[i])

    # LOAD JOURNAL INTO BEAUTIFULSOUP
    print("url =", journal_URL)
    while True:
        try:
            html = urlopen(journal_URL)
            if html.getcode() == 200:
                break;
        except Exception as inst:
            print("Exception at", journal_URL,":", inst)
    bs = BeautifulSoup(html.read(), 'html.parser')

    # PARSE VOLUMES FROM JOURNAL PAGE
    volumes = bs.contents[2].contents[3].contents[9]
    volumes_URLs = []
    volumes_names = []

    for index in range(3, len(volumes), 2):
        volume_URI = volumes.contents[index].contents[3].contents[1].contents[0].contents[0]['href']
        volume_URL = urijoin(journal_URL, volume_URI)
        volumes_URLs.append(volume_URL)
        volumes_names.append(volumes.contents[index].contents[3].contents[1].contents[0].contents[0].string)

    # ITERATE ON VOLUME PAGES
    startIndex = 0
    for index in range(startIndex, len(volumes_URLs)):
        while True:
            try:
                html = urlopen(volumes_URLs[index])
                if html.getcode() == 200:
                    break;
            except Exception as inst:
                print("Exception at", volumes_URLs[index],":", inst)
        bs = BeautifulSoup(html.read(), 'html.parser')

        # PARSE ARTICLES FROM VOLUME PAGE
        try:
            articles = bs.contents[2].contents[3].contents[15].contents[3]
        except Exception as inst:
            print("Exception at", volumes_URLs[index],":", inst)
            continue

        # ITERATE ON ARTICLES
        for article_num in range(1, len(articles), 2):
            if mirror == "Libgen":
                try:
                    article_URL = articles.contents[article_num].contents[9].contents[0].contents[1].contents[0]['href']
                except Exception as inst:
                    print("Exception at", article_URL,":", inst)
                    continue
                while True:
                    try:
                        html = urlopen(article_URL)
                        if html.getcode() == 200:
                            break;
                    except Exception as inst:
                        print("Exception at", article_URL,":", inst)
                article_bs = BeautifulSoup(html.read(), 'html.parser')
                print("article_URL =", article_URL)

                # DOWNLOAD ARTICLE
                try:
                    get_URL = urijoin('http://libgen.gs', article_bs.find(href=re.compile("(get)"))['href'])
                except Exception  as inst:
                    print("Exception at", article_URL,":", inst)
                    continue

            elif mirror == "Sci-Hub":
                article_URL = articles.contents[article_num].contents[9].contents[0].contents[0].contents[0]['href']
                html = urlopen(article_URL)
                article_bs = BeautifulSoup(html.read(), 'html.parser')
                try:
                    print(str(article_bs.contents[2].contents[3].contents[7].contents[3].contents[1]).split('"')[1].replace("location.href='", ""))
                except Exception as inst:
                    print("Exception:", inst)

                # DOWNLOAD ARTICLE
                get_URI = article_bs.contents[2].contents[2].contents[2].contents[1].contents[3].contents[0]['href']
                get_URL = urijoin('http://libgen.gs', get_URI)

            # DOWNLOAD ARTICLE IN LOCAL DIR
            failure = True

            attempts = 0
            while failure:
                try:
                    filename = wget.download(get_URL)
                    failure = False
                except Exception as inst:
                    print("Exception:", inst)
                    failure = True
                    try:
                        if inst.errno == 36:
                            failure = False
                    except Exception as errno:
                        print("Exception: no errno.")
                        failure = True
                        break
                    attempts += 1
                    if attempts >= 24:
                        failure = False

            if failure:
                continue
            

            # MOVE FILE TO JOURNAL DIR
            volume = volumes_names[index]
            if os.path.isdir(outputs[i]) == False:
                os.mkdir(outputs[i])
            if os.path.isdir(outputs[i] + volume) == False:
                os.mkdir(outputs[i] + volume)
            if os.path.isfile("./"+filename) == True:
                if len(filename) >= 250:
                    fileExt = filename.split(".")[-1]
                    filename = splitAtIndex(filename, 245) + fileExt
                filenameNew = outputs[i] + volume + '/' + filename
                try:
                    shutil.move(filename, filenameNew)
                except Exception as inst:
                    print("Exception:", inst, "\nFilename length =", len(filename))
