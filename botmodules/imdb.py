import re
import sys

def get_imdb(self, e, urlposted=False):
    #reads title, rating, and movie description of movie titles
    searchterm = e.input
    if urlposted:
        url = searchterm
    else:
        url = self.tools['google_url']("site:imdb.com inurl:com/title " + searchterm, "imdb.com/title/tt\\d{7}/")

    if url.find("imdb.com/title/tt") != -1:
        movietitle = ""
        rating = ""
        summary = ""
        imdbid = re.search("tt\\d{7}", url)
        imdburl = 'http://www.imdb.com/title/' + imdbid.group(0) + '/'
        page = self.tools["load_html_from_url"](imdburl)

        movietitle = page.html.head.title.string.replace(" - IMDb", "")
        movietitle = movietitle.replace("IMDb - ", "")
        movietitle = "Title: " + movietitle

        if page.find("div", {"class":"title-overview"}) != None:
            page = page.find("div", {"class":"title-overview"}).extract()

            if page.find("span", itemprop="ratingValue") != None:
                rating = page.find("span", itemprop="ratingValue").text
                rating = " - Rating: " + rating.replace("\n", "")  # remove newlines since BS4 adds them in there


            summary = str(page.find("div", {"class":"summary_text"}, itemprop="description"))

            summary = re.sub(r'\<a.*\/a\>', '', summary)
            summary = self.tools['remove_html_tags'](summary)
            summary = summary.replace('&raquo;', "")
            summary = summary.replace("\n", "")
            summary = summary.strip()
            summary = " - " + summary



        title = movietitle + rating + summary
        if not urlposted:
            title = title + " [ %s ]" % url

        e.output = title

        return e
get_imdb.command = "!imdb"
get_imdb.helptext = "Usage: !imdb <movie title>\nExample: !imdb the matrix\nLooks up a given movie title on IMDB and shows the movie rating and a synopsis"
 
