import CCDataGatherer as CCrawl
import TextConverter as CC_HTML_Parser
import NYTData as NYTimes

if __name__ == '__main__':

    keywords = ["global-warming", "drought", "extreme-weather", "hurricane", "pollution", "sea-level-rise"]
    INDEX_LIST = ["2019-04", "2019-09", "2019-13"]
    DOMAIN_LIST = ["climate.nasa.gov", "globalchange.gov", "insideclimatenews.org", "ipcc.ch", "350.org",
                   "public.wmo.int/en", "greenpeace.org/usa/"]

    CCrawl.handler(keywords=keywords, INDEX_LIST=INDEX_LIST, DOMAIN_LIST=DOMAIN_LIST)
    CC_HTML_Parser.handler()
    
    NYTimes.handler()
