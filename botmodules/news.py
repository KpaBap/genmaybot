import urllib, urllib.request, urllib.error, urllib.parse, xml.dom.minidom, datetime, json
from bs4 import BeautifulSoup
from email.utils import parsedate
import time


def get_newest_rss(self, url):
## Retreive an RSS feed and get the newest item
## Then, nicely format the title and description, and add a shortened URL

    dom = xml.dom.minidom.parse(urllib.request.urlopen(url))
    newest_news = dom.getElementsByTagName('item')[0]
    title = newest_news.getElementsByTagName('title')[0].childNodes[0].data
    description = BeautifulSoup(newest_news.getElementsByTagName('description')[0].childNodes[0].data, "html.parser")

    updated = dom.getElementsByTagName('pubDate')[0].childNodes[0].data
    updated = datetime.datetime.fromtimestamp(time.mktime(parsedate(updated)))
    ago = round((datetime.datetime.utcnow() - updated).seconds/60)



    links = description.findAll('a')
    for link in links:
        link.extract()
    links = description.findAll(color='#6f6f6f')
    for link in links:
        link.extract()

    title = title.strip()

    description = str(description)
    description = description.replace("\n", "")

    description = self.tools['remove_html_tags'](description)
    description = description.strip()
    if description.rfind(".") != -1:
        description = description[0:description.rfind(".") + 1]

    link = self.tools['shorten_url'](newest_news.getElementsByTagName('link')[0].childNodes[0].data)

    description = "%s - %s [ %s ]" % (title, description, link)

    return description, updated, ago


def google_news(self, e):
    query = urllib.parse.quote(e.input)
    url = ""
    if not query:
        url = "https://news.google.com/news/rss/?gl=US&ned=us&hl=en"

    else:
        url = "https://news.google.com/news/rss/search/section/q/%s/?hl=en&gl=US&ned=us" % query

    description, updated, ago = get_newest_rss(self,url)

    e.output = description

    return e

google_news.command = "!news"
google_news.helptext = "Usage: !news - reports the top story. !news <query> reports news containing the specified words"

def get_breaking(self, e):
    pass

def breaking_alert():
    pass

def npr_science(self, e):
    ## Grab the latest entry from the NPR Health and Science RSS feed
    url = "http://www.npr.org/rss/rss.php?id=1007"
    description, updated, ago = get_newest_rss(self,url)
    e.output = description
    return e

npr_science.command="!npr-sci"
npr_science.helptext="Usage: !npr-sci\nShows the latest entry from the NPR Health and Science RSS feed"

def npr_most_emailed(self, e):
    ## Grab the latest entry from the NPR Most Emailed RSS feed
    url = "http://www.npr.org/rss/rss.php?id=100"
    description, updated, ago = get_newest_rss(self,url)
    e.output = description
    return e

npr_most_emailed.command="!npr-top"
npr_most_emailed.helptext="Usage: !npr-top\nShows the latest entry from the NPR Most Emailed RSS feed"

def npr_headlines(self, e):
    ## Grab the latest entry from the NPR headlines RSS feed
    url = "http://www.npr.org/rss/rss.php?id=1001"
    description, updated, ago = get_newest_rss(self,url)
    e.output = description
    return e

npr_headlines.command="!npr"
npr_headlines.helptext="Usage: !npr\nShows the latest entry from the NPR headlines RSS feed"

def npr_music(self, e):
## Get the latest song of the day from NPR First Listen
    url = "http://api.npr.org/query?id=98679384&fields=title,teaser,audio&dateType=story&sort=dateDesc&output=JSON&numResults=1&apiKey=%s" % ( self.botconfig["APIkeys"]["nprAPIkey"])

    response = urllib.request.urlopen(url).read().decode('utf-8')
    musicdata = json.loads(response)
    musicdata = musicdata['list']['story'][0]

    teaser = musicdata['teaser']['$text']
    teaser = teaser.replace("\"","")

    for links in musicdata['link']:
        if links['type'] == "short":
                link = links['$text']
                break

    title = musicdata['title']['$text']
    e.output = "%s - %s [ %s ]" % (title,teaser,link)
    e.output = e.output.replace("<em>","'")
    e.output = e.output.replace("</em>","'")
    e.output = e.output.replace("First Listen: ","") #Unnecessary spam

    return e

npr_music.command="!music"
npr_music.helptext="Usage: !music\nShows the latest music listing from NPR's Discover Music song of the day"
