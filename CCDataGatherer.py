import requests
import json


def getURLMetadata(CC_URL, keyword):
    """
    This function searches the Common Crawl dataset for the domain and index passed in the URL.
    We have added a filter to the data which will only store the links if the links contain
    any of the keywords that we desire.

    :param CC_URL: The API URL used to query data from Common Crawl dataset
    :param keyword: The desired keyword whose presence in the links is necessary to
                      store them
    :return: Returns a list of JSON objects which contain the metadata for the filtered links
    """

    record_list = []
    response = requests.get(url=CC_URL)

    # Following block is used to ensure that the multiword keywords like Global Warming
    # are included in all possible ways in the links. Since web links cannot contain whitespaces,
    # the spaces can be filled by a special character like hyphen(-) or underscore(_) or plus(+)
    # symbols. This block ensures to include such characters in the search terms to get more data
    # for the same keyword.
    keywordList = []
    if "-" in keyword:
        keywordList.append(keyword)
        keywordList.append(keyword.split("-")[0] + "_" + keyword.split("-")[1])
        keywordList.append(keyword.split("-")[0] + "+" + keyword.split("-")[1])
    else:
        keywordList.append(keyword)

    if response.status_code == 200:
        records = response.content.splitlines()
        for record in records:
            data = json.loads(record)
            if "languages" in data.keys():
                if any(subkeyword in data["url"] for subkeyword in keywordList) and data["languages"] == "eng":
                    record_list.append(data)
            else:
                if any(subkeyword in data["url"] for subkeyword in keywordList):
                    record_list.append(data)
    print("[*] Found a total of %d hits." % len(record_list))

    return record_list, len(record_list)


def queryURLs(keyword, INDEX_LIST, DOMAIN_LIST):
    """
    This function acts as the driver to the getURLMetadat function. It defines the list of indices to
    search from the Common Crawl Dataset and the list of domains through which it should search.
    It also sets the restrictions of number of links to be searched after which the control moves to
    the next keyword. It also defines the list of keywords to be searched in the links.

    :return: Returns a list of dict type. The dicts contain the metadata of the articles found on
             crawlers indices.
    """

    # For big data
    ARTICLES_PER_KEYWORD = 150

    # For small data for word co occurances
    # ARTICLES_PER_KEYWORD = 7

    records = []
    count = 0

    # For Big data
    file_name = ".\\Data\\ccdata_" + keyword + ".json"

    # For small data for word co occurances
    # file_name = "ccdata_" + keyword + "pair.json"

    for INDEX in INDEX_LIST:
        for DOMAIN in DOMAIN_LIST:
            CC_URL = "http://index.commoncrawl.org/CC-MAIN-%s-index?" % INDEX
            CC_URL += "url=%s&matchType=domain&output=json" % DOMAIN
            recList, hits = getURLMetadata(CC_URL, keyword)
            count += hits
            if count > ARTICLES_PER_KEYWORD:
                break
            records.append(recList)
        records = [rec for rec in records]
        if count > ARTICLES_PER_KEYWORD:
            break
    records = [rec for re in records for rec in re]
    print("For keyword " + keyword + " found " + str(count) + " articles.")
    with open(file_name, 'w') as jsonFile:
        jsonFile.write(json.dumps(records, sort_keys=True, indent=4, separators=(',', ': ')))

    return records


def handler(keywords, INDEX_LIST, DOMAIN_LIST):
    """
    This function acts as the entry point to the program. It defines the keywords to be used in search

    :param keywords: List of words around which articles are to be found
    :param INDEX_LIST: Indices to search the data from. The indices are year and week in YYYY-WW format
    :param DOMAIN_LIST: List of base URLs to query the keywords from

    :return: nothing
    """

    for keyword in keywords:
        records = queryURLs(keyword, INDEX_LIST, DOMAIN_LIST)
