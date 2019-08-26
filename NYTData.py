from bs4 import BeautifulSoup
import requests
import json
import math
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))


def getArticlesMetadata(apikey, query, begin_date, page):
    """
    This function is used to hit the article search API of NY Times and get the metadata results in JSON format

    :param apikey: The API Key obtained from developer.nytimes.com for the search API
    :param query:  The topic for which articles are to be searched
    :param begin_date: Date from which the search API should look for the articles. The date here is the date of publication of the article
    :param page: The page of the search results to display. Each page can display a maximum of 10 articles. Refer: https://developer.nytimes.com/docs/articlesearch-product/1/overview
    :return: returns a JSON object of type dict which contains metadata of up to 10 articles on the search query.
    """

    # Build the URL for get request with the passed parameters
    URL = "https://api.nytimes.com/svc/search/v2/articlesearch.json?facet=true&begin_date=" + begin_date + "&q=" + query + "&api-key=" + apikey + "&page=" + page
    response = requests.get(url=URL)
    data = response.json()

    # Create a dynamic name for a file to store the JSON results.
    FILE = query + page + ".json"

    if response.status_code == 200:
        if data["response"]["meta"]["hits"] > 0:
            # Check if the response contains any articles and dump the received metadata into a JSON file
            with open(FILE, "w") as file:
                file.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))

    return data, data["response"]["meta"]["hits"]


def getArticleText(data, articleNumber):
    """
    This function is used to fetch an HTML document pointed by the URL mentioned in the JSON file for each article.
    This HTML document is then broken down to extract the text from the webpage. The same text is returned as the
    output of the function.

    :param data: The JSON object which contains the metadata of the article
    :param articleNumber: The specific article form the JSON object which is to be parsed
    :return: returns textdata of type string
    """

    web_url = data["response"]["docs"][articleNumber]["web_url"]
    response1 = requests.get(web_url)
    soup = BeautifulSoup(response1.text, 'html.parser')

    textData = ""

    # Following block parses the HTML tags to filter the text.
    # NYTimes webpages have a consistent and unique nomenclature for the classes of its HTML tags.
    # We have used the same classnames to extract the tags which contain text data.
    if soup.find('section', attrs={"name": "articleBody"}) is not None:
        sections = soup.find('section', attrs={"name": "articleBody"}).find_all('div', attrs={
            "class": "css-1fanzo5 StoryBodyCompanionColumn"})

        for div in sections:
            divsdata = (div.find_all('p', attrs={"class": "css-1ygdjhk evys1bk0"}))
            for element in divsdata:
                textData += element.text

    return textData


def handler():
    """
    This function is used as a driver for the code. The parameters used in the code are set here.

    :return: nothing
    """
    query = "global warming"  # drought extreme weather, global warming, hurricane, pollution, sea level rise
    begin_date = "20190101"
    API_KEY = "Your_API_Key_Goes_Here"

    # Number of articles required. This is used to calculate the number of pages that will be accessed by the code
    ARTICLES = 100

    # The file where the extracted text is to be stored
    TEXT_FILE = ".\\Data\\nytdata_"+query + ".txt"

    # A counter which checks the obtained articles
    articleCount = 0
    text = ""

    # This loop calculates the number of pages required to fetch all the results
    # and iterates over each page to fetch the data
    for pgNumber in range(int(math.ceil(ARTICLES / 10))):
        data, hits = getArticlesMetadata(API_KEY, query, begin_date, str(pgNumber))

        # In some cases, the number of found articles can be less than the desired value.
        # This check updates the article count to the new value in such scenario
        if hits < ARTICLES:
            ARTICLES = hits

        for pageCount in range(len(data["response"]["docs"])):
            text += getArticleText(data, pageCount) + "\n\n"
            articleCount += 1

    print(str(articleCount) + " articles found")
    with open(TEXT_FILE, 'w', encoding="utf-8") as file:
        tokens = nltk.tokenize.word_tokenize(text)
        cleanTokens = [word for word in tokens if word not in stop_words]
        text =""
        for word in cleanTokens:
            # word = nltk.PorterStemmer().stem(word)
            word = nltk.wordnet.WordNetLemmatizer().lemmatize(word)
            if word not in ["n't", ",", "-", ".", "'", "...","’","—","”","“",":"]:
                text += word+"\n"
        file.write(text)