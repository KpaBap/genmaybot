import json, urllib.request, urllib.error, urllib.parse, random
def get_cat(self, e):
    url = "http://www.reddit.com/r/catpictures+cats/.json"
    e.output = get_redditpics(url)
    return e
get_cat.command = "!cats"

def get_dvq(self, e):
    e.output = "http://i.imgur.com/1lq54.jpg"
    return e
get_dvq.command = "!dvq"

def get_fern(self, e):
    e.output = "http://i.imgur.com/TNIt1.jpg"
    return e
get_fern.command = "!fern"


def get_rat(self, e):
    url = "http://www.reddit.com/r/rats/.json"
    e.output = get_redditpics(url)
    return e
get_rat.command = "!rats"

def get_dog(self, e):
    url = "http://www.reddit.com/r/dogpictures+dogs/.json"
    e.output = get_redditpics(url)
    return e
get_dog.command = "!dogs"

def get_bird(self, e):
    url = "http://www.reddit.com/r/birdpics/.json"
    e.output = get_redditpics(url)
    return e
get_bird.command = "!birds"

def get_cacti(self, e):
    url = "http://www.reddit.com/r/cacti/.json"
    e.output = get_redditpics(url)
    return e
get_cacti.command = "!cacti"

def get_sloth(self, e):
    url = "http://www.reddit.com/r/sloths/.json"
    e.output = get_redditpics(url)
    return e
get_sloth.command = "!sloths"

def get_sandwich(self, e):
    url = "http://www.reddit.com/r/eatsandwiches/.json"
    e.output = get_redditpics(url)
    return e
get_sandwich.command = "!sandwiches"

def get_rpics(self, e):
    if not e.input:
        e.input = "pics"
    elif "clop" in e.input:
        self.irccontext.kick(e.source, e.nick, "No clop allowed!")
        return e
    url = "http://www.reddit.com/r/%s/.json" % e.input
    e.output = get_redditpics(url)
    return e
get_rpics.command = "!rpics"

def get_redditpics(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'genmaybot IRC bot')]
    response = opener.open(url).read()
    cats = json.loads(response.decode('utf-8'))
    catlist = []
    for cat in cats['data']['children']:
        if 'jpg' in cat['data']['url'] or 'imgur.com' in cat['data']['url']:
            pic_title = cat['data']['title']
            pic_title = pic_title.replace('\n', '')
            if cat['data']['over_18']:
                pic_title = "=NSFW= " + pic_title
            catlist.append(cat['data']['url'] + " - " + pic_title)

    cats = catlist.pop(random.randint(0, len(catlist) - 1)) + " :: " + catlist.pop(random.randint(0, len(catlist) - 1))
    return cats

def get_roznalos(self, e):
    e.output = "https://i.imgur.com/KAbGott.jpg"
    return e
get_roznalos.command ="!roznalos"
get_roznalos.helptext = "Poor roznalos!"

def get_gumby(self, e):
    e.output = "http://imgur.com/Es8FioK"
    return e
get_gumby.command ="!gumby"
get_gumby.helptext = "D'awww!"

def get_grimace(self, e):
    e.output = "https://i.imgur.com/yyvBaOC.jpg"
    return e
get_grimace.command = "!grimace"


def faptain(self, e):
    e.output = "FaptainAwesome to the rescue!"
    return e

faptain.command = "!fap"

def epoop(self, e):
    e.output = "https://i.imgflip.com/2el2zw.jpg"
    return e

epoop.command = "!epon"

