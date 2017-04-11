
def get_metacritic(self, e):
    url = self.tools['google_url']("site:metacritic.com " + e.input, "www.metacritic.com/")
    page = self.tools["load_html_from_url"](url)
    title_div = page.findAll('div', attrs={"class": "product_title"})[0]
    try:
        title = title_div.a.span.string.strip()
    except:  # tv shows have an extra span
        title = ""
        for string in title_div.a.stripped_strings:
            title = title + string
    title_url = title_div.a['href']
    if title_url.find("game/") > 0:
        category = 'Game - '
        category += title_div.findAll('span', attrs={"class": "platform"})[0].a.span.string.strip()
    elif title_url.find("movie/") > 0:
        category = "Movie"
    elif title_url.find("tv/") > 0:
        category = "TV"
    elif title_url.find("music/") > 0:
        category = "Music"
        # band name is here, append it to title
        title += " " + title_div.findAll('span', attrs={"class": "band_name"})[0].string

    if category:
        category = "(%s) " % category

    # declare these to avoid null reference
    meta_score = ""
    user_score = ""

    meta_score_div = page.findAll('div', attrs={"class": "metascore_wrap highlight_metascore"})[0]
    meta_score = meta_score_div.findAll('span', attrs={"itemprop": "ratingValue"})[0].string
    meta_desc = meta_score_div.findAll('span', attrs={"class": "desc"})[0].string.strip()
    meta_num = meta_score_div.findAll('span', attrs={"itemprop": "reviewCount"})[0].string.strip()

    user_score_div = page.findAll('div', attrs={"class": "userscore_wrap feature_userscore"})[0]
    user_score = user_score_div.a.div.string
    user_desc = user_score_div.findAll('span', attrs={"class": "desc"})[0].string
    user_num = user_score_div.find('span', attrs={"class": "count"}).a.string

    if meta_score:
        meta_score = "Metascore: " + meta_score
        meta_score += " out of 100 - %s (%s Reviews)" % (meta_desc.strip(), meta_num.strip())
        meta_score = "%s | " % meta_score
    if user_score:
        user_score = "User Score: " + user_score
        user_score += " out of 10 - %s (%s)" % (user_desc.strip(), user_num.strip())

    if meta_score or user_score:
        e.output = "%s %s| %s%s" % (title, category, meta_score, user_score)
    return e

get_metacritic.command = "!mc"

