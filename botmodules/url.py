# coding=utf-8

import re
import hashlib
import datetime
import sqlite3


def url_parser(self, e):
    url = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>])*\))+(?:\(([^\s()<>])*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", e.input)
    #http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    if url:
        url = url.group(0)
        if url[0:4].lower() != "http":
            url = "http://" + url
        e.input = url
        return url_posted(self, e)
    else:
        return None
url_parser.lineparser = True


def url_posted(self, e):
    url = e.input
    #checks if the URL is a dupe (if mysql is enabled)
    #detects if a wikipedia or imdb url is posted and does the appropriate command for it

    repost = ""
    days = ""

    urlhash = hashlib.sha224(url.encode()).hexdigest()
    conn = sqlite3.connect("links.sqlite")
    cursor = conn.cursor()
    result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='links';").fetchone()
    if not result:
        cursor.execute('''CREATE TABLE 'links' ("url" tinytext, "hash" char(56) NOT NULL UNIQUE, "reposted" smallint(5) default '0', "timestamp" timestamp NOT NULL default CURRENT_TIMESTAMP);''')
        cursor.execute('''CREATE INDEX "links_hash" ON 'links' ("hash");''')

    query = "SELECT reposted, timestamp FROM links WHERE hash='%s'" % urlhash
    result = cursor.execute(query)
    result = cursor.fetchone()
    if result:
        repost = "LOL REPOST %s " % (result[0] + 1)

        orig = datetime.datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.utcnow()
        delta = now - orig

        plural = ""
        if delta.days > 0:
            if delta.days > 1:
                plural = "s"
            days = " (posted %s day%s ago)" % (str(delta.days), plural)
        else:
            hrs = int(round(delta.seconds / 3600.0, 0))
            if hrs == 0:
                mins = round(delta.seconds / 60)
                if mins > 1:
                    plural = "s"
                days = " (posted %s minute%s ago)" % (str(mins), plural)
                if mins == 0:
                    repost = ""
                    days = ""
            else:
                if hrs > 1:
                    plural = "s"
                days = " (posted %s hour%s ago)" % (str(hrs), plural)

    title = ""

    try:
        wiki = self.bangcommands["!wiki"](self, e, True)
        title = wiki.output
    except:
        pass
    try:
        imdb = self.bangcommands["!imdb"](self, e, True)
        title = imdb.output
    except:
        pass
    try:
        yt = self.bangcommands["!yt"](self, e, True)
        if yt:
            title = yt.output
    except:
        pass
    try:
        trope = self.bangcommands["!trope"](self, e, True)
        if trope:
            title = trope.output
    except:
        pass
    if url.find("imgur.com") != -1 and url.find("/a/") == -1 and "/gallery/" not in url:
        imgurid = url[url.rfind('/') + 1:]
        if "." in imgurid:
            imgurid = imgurid[:imgurid.rfind('.')]
        url = "http://imgur.com/" + imgurid

    # Ignore strava ride links because Dan said so, fuck modularity, embace tight coupling.
    if url.find("app.strava.com/activities") != -1 or url.find("www.strava.com/activities") != -1:
        return None
    if not title:
        title = get_title(self, e, url)

    if title:
        if "imgur:" in title.lower():
            title = ""
        title = title.replace("\n", " ")
        title = re.sub('\s+', ' ', title)
        title = re.sub('(?i)whatsisname', '', title)

        cursor.execute("""UPDATE OR IGNORE links SET reposted=reposted+1 WHERE hash = ?""", [urlhash])
        cursor.execute("""INSERT OR IGNORE INTO links(url, hash) VALUES (?,?)""", (url, urlhash))
        conn.commit()

        e.output = "%s%s%s" % (repost, title, days)

    conn.close()

    return e


def get_title(self, e, url):
    length = 51200
    if url.find("amazon.") != -1:
        length = 100096  # because amazon is coded like shit
    page = self.tools["load_html_from_URL"](url, length)
    title = ""
    meta_title = ""

    if page and page.find('meta', attrs={'name': "generator", 'content': re.compile("MediaWiki", re.I)}):
        try:
            wiki = self.bangcommands["!wiki"](self, e, True, True)
            title = wiki.output
        except:
            pass
    elif page:
        title = "Title: " + page.find('title').string
        try:
            meta_title = "Title: " + page.find('meta', attrs={'property': "og:title"}).get("content")
        except:
            meta_title = ""
        
        
    if meta_title:
        return meta_title
    else:
        return title


def last_link(self, e):
    #displays last link posted (requires mysql)
    conn = sqlite3.connect("links.sqlite")
    cursor = conn.cursor()
    if cursor.execute("SELECT url FROM links ORDER BY rowid DESC LIMIT 1"):
        result = cursor.fetchone()
        url = result[0]

    conn.close()
    e.output = "[ " + url + " ] " + get_title(self, e, url)
    return e

last_link.command = "!lastlink"
last_link.helptext = "Usage: \002!lastlink\002" \
                     "Shows the last URL that was posted in the channel"
