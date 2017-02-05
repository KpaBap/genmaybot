import json
import urllib.request
import re


def ytinfo(self, e, urlposted=False):
    if urlposted:
        yt = e.input
        if "youtube.com" not in yt and "youtu.be" not in yt:
            return
        yt = re.search("(v=|/)([\w-]+)(&.+|#t=.+|\?t=.+)?$", yt).group(2)
    else:
        yt = self.tools['google_url']('site:youtube.com {}'.format(e.input), 'watch\?v=')
        self.logger.debug(yt)
        yt = yt[yt.find("?v=") + 3:]

    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2C+contentDetails%2C+statistics&hl=en&id={}&key={}"
    url = url.format(yt, self.botconfig["APIkeys"]["shorturlkey"])

    request = urllib.request.urlopen(url)
    ytjson = json.loads(request.read().decode())
    ytjson = ytjson['items'][0]
    
    duration = ytjson['contentDetails']['duration']
    duration = duration[2:].lower()

    try:
        likes = int(ytjson['statistics']['likeCount'])
        self.logger.debug(likes)
        dislikes = int(ytjson['statistics']['dislikeCount'])
        self.logger.debug(dislikes)
        rating = "{0:.1f}/10".format((likes / (likes + dislikes)) * 10)
    except:
        rating = "NA"
    
    ytlink = ""
    if not urlposted:
        ytlink = " - http://youtu.be/" + yt

    content = ""
    try:
        if ytjson['contentDetails']['contentRating']:
            content = " - 4NSFW"
    except KeyError:
        pass

    title = ytjson['snippet']['title']
    uploader = ytjson['snippet']['channelTitle']
    pubdate = ytjson['snippet']['publishedAt'][:10]
    viewcount = ytjson['statistics']['viewCount']


    #All this just to get the category....
    catid = ytjson['snippet']['categoryId']
    url = "https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&hl=en&id={}&key={}"
    url = url.format(catid, self.botconfig["APIkeys"]["shorturlkey"])
    request = urllib.request.urlopen(url)
    ytjson2 = json.loads(request.read().decode())
    category = ytjson2['items'][0]['snippet']['title']


    e.output = "Youtube: {} [{}] :: length: {} - rated: {} - {} views - {} on {}{}{}".format(title,
                                                                                            category,
                                                                                            duration,
                                                                                            rating,
                                                                                            viewcount,
                                                                                            uploader,
                                                                                            pubdate,
                                                                                            ytlink, content)
    return e
ytinfo.command = "!yt"
ytinfo.helptext = """
Usage: !yt <vide title>
Example: !yt cad video
Looks up a given youtube video, and provides information and a link"""
