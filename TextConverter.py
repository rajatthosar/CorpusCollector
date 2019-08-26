from bs4.element import Comment
from bs4 import BeautifulSoup
import requests
import json
import os


def getFilePaths(DIRPATH):
    """
    This function returns the relative paths of the files present in the directory
    pointed by the DIRPATH variable.

    :param DIRPATH: The path to the directory where files are needed to be searched
    :return: returns a list of string type. This list contains the paths to the files
             present in the directory.
    """
    filelist = []
    for dir_, _, files in os.walk(DIRPATH):
        for file_name in files:
            if file_name.split(".")[1] == "json":
                rel_file = os.path.join(file_name)
                filelist.append(rel_file)

    return filelist


def tag_visible(element):
    """
    This function acts as a filter to exclude HTML formatters. It would skip the
    elements mentioned in the below list and parse only the visible text.

    :param element: The tag which is to be parsed
    :return: returns a boolean type
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def getHTMLData(file):
    """
    This function fetches HTML page for the URL mentioned in the file and parses its tags
    to mine text data from them.

    :param file: The JSON file which contains the URL which points to an HTML page
    :return: returns textdata of string type. This textdata is the visible text on the HTML page
    """

    textdata = ""

    with open(file, 'r', encoding="utf-8") as jsonFile:
        data = json.loads(jsonFile.read())

    for element in data:
        url = element["url"]
        response = requests.get(url=url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texts = soup.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            textdata += u" ".join(t.strip() for t in visible_texts)

    return textdata


def handler():
    """
    This function acts as the entry point to the program

    :return: nothing
    """

    DIRPATH = ".\\Data\\"
    files = getFilePaths(DIRPATH)
    for file in files:
        filename = file.split(".")[0] + ".txt"
        text = getHTMLData(file)
        with open(filename,'w', encoding="utf-8") as textFile:
            textFile.write(text+"\n\n")