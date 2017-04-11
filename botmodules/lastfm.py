# -*- coding: utf-8 *-*
import sqlite3
import urllib
import json


def setlastfmuser(self, e):
    conn = sqlite3.connect('lastfm.sqlite')
    c = conn.cursor()
    result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lastfm';").fetchone()
    if not result:
        c.execute('''create table lastfm(user text UNIQUE ON CONFLICT REPLACE, lastfmuser text)''')

    c.execute("""insert into lastfm values (?,?)""", (e.nick.lower(), e.input))
    conn.commit()
    c.close()
setlastfmuser.command = "!setlastfm"
setlastfmuser.helptext = """Usage: !setlastfm <last.fm username>
Example: !setlastfm jbeiber
Sets your last.fm username so you can use the !np and !compare commands without needing to provide your username"""

def nowplaying(self, e):
    conn = sqlite3.connect('lastfm.sqlite')
    c = conn.cursor()
    try:
        if e.input:
            lastfmuser = c.execute("SELECT lastfmuser FROM lastfm WHERE user = LOWER(?)", [e.input]).fetchone()
            if not lastfmuser:
                lastfmuser = [e.input]
        else:
            lastfmuser = c.execute("SELECT lastfmuser FROM lastfm WHERE user = LOWER(?)", [e.nick]).fetchone()
    except sqlite3.OperationalError:
        self.logger.info("Defaulting last.fm username to nickname for {} and retrying.".format(e.nick))
        e.input = e.nick
        setlastfmuser(self, e)
        return nowplaying(self,e)

    if lastfmuser:
        lastfmuser = lastfmuser[0]
        url = "http://ws.audioscrobbler.com/2.0/?api_key=%s&limit=1&format=json&method=user.getRecentTracks&user=%s" % (self.botconfig["APIkeys"]["lastfmAPIkey"], lastfmuser)
        print ("Getting lastfm url: {}".format(url))
        response = urllib.request.urlopen(url).read().decode('utf-8')
        track = json.loads(response)
        try:
            artist = track['recenttracks']['track'][0]['artist']['#text']
            trackname = track['recenttracks']['track'][0]['name']
            try:
                trackinfo = get_trackinfo(self.botconfig["APIkeys"]["lastfmAPIkey"], artist, trackname, lastfmuser)
                artist = trackinfo['artist']['name']
                trackname = trackinfo['name']
            except:
                pass
            try:
                dmin, dsec = divmod(int(trackinfo['duration']) / 1000, 60)
                duration = " [{:.0f}:{:02.0f}]".format(dmin, dsec)
            except:
                duration = ""
            try:
                playcount = " :: Playcount: %s" % trackinfo['userplaycount']
            except:
                playcount = ""
            try:
                genres = []
                for genre in trackinfo['toptags']['tag']:
                    genres.append(genre['name'])
                genres = " (%s)" % ", ".join(genres)
            except:
                genres = ""
            try:
                yt = self.tools['google_url']('site:youtube.com %s - %s' % (artist, trackname), 'watch%3Fv%3D')
                yt = yt[yt.find("%3Fv%3D") + 7:]
                yt = " - http://youtu.be/" + yt
            except:
                yt = ""
            e.output = "%s np: %s - %s%s%s%s%s" % (lastfmuser, artist, trackname, duration, playcount, genres, yt)
        except:
            #an exception means they are not currently playing a track
            artist = track['recenttracks']['track']['artist']['#text']
            trackname = track['recenttracks']['track']['name']
            played = track['recenttracks']['track']['date']['#text']
            try:
                yt = self.tools['google_url']('site:youtube.com %s - %s' % (artist, trackname), 'watch%3Fv%3D')
                yt = yt[yt.find("%3Fv%3D") + 7:]
                yt = " - http://youtu.be/" + yt
            except:
                yt = ""
            e.output = "%s is not playing a track, but last played: %s - %s on %s%s" % (lastfmuser, artist, trackname, played, yt)
    else:
        e.output = "You don't have a last.fm user set up - use !setlastfm <username>"

    return e
nowplaying.command = "!np"
nowplaying.helptext = """Usage: !np or !np <last.fm username/IRC nick>
Example: !np
Shows your currently playing trak on last.fm. To use !np without arguments your username must be set up first with !setlastfm"""


def get_trackinfo(apikey, artist, trackname, userid):
    artist = urllib.parse.quote(artist)
    trackname = urllib.parse.quote(trackname)
    url = "http://ws.audioscrobbler.com/2.0/?api_key=%s&format=json&method=track.getInfo&artist=%s&track=%s&username=%s" % (apikey, artist, trackname, userid)
    response = urllib.request.urlopen(url).read().decode('utf-8')
    track = json.loads(response)
#    self.logger.debug(track)
    return track['track']

def compare(self, e):
    conn = sqlite3.connect('lastfm.sqlite')
    c = conn.cursor()
    user1 = ""
    user2 = ""

    if len(e.input.split(" ")) == 1:
        lastfmuser = c.execute("SELECT lastfmuser FROM lastfm WHERE user = LOWER(?)", [e.nick]).fetchone()
        if lastfmuser:
            user1 = lastfmuser[0]
            #first check if we're copmaring against an irc user - if there's a hit it's assumed so
            compuser = c.execute("SELECT lastfmuser FROM lastfm WHERE user = LOWER(?)", [e.input]).fetchone()
            if compuser:
                user2 = compuser[0]
            else:
                user2 = e.input
        else:
            e.output = "you don't have a last.fm user set up - use !setlastfm <username>"
    elif len(e.input.split(" ")) == 2:
        var1 = e.input.split(" ")[0]
        var2 = e.input.split(" ")[1]
        lastfmuser = c.execute("SELECT lastfmuser FROM lastfm WHERE user = LOWER(?)", [var1]).fetchone()
        if lastfmuser:
            user1 = lastfmuser[0]
        else:
            user1 = var1
        lastfmuser = c.execute("SELECT lastfmuser FROM lastfm WHERE user = LOWER(?)", [var2]).fetchone()
        if lastfmuser:
            user2 = lastfmuser[0]
        else:
            user2 = var2

    if user1 and user2:
        url="http://ws.audioscrobbler.com/2.0/?api_key=%s&method=tasteometer.compare&type1=user&type2=user&value1=%s&value2=%s&format=json" % (self.botconfig["APIkeys"]["lastfmAPIkey"], user1, user2)
        response = urllib.request.urlopen(url).read().decode('utf-8')
        match = json.loads(response)
        score = "{:.2%}".format(float(match['comparison']['result']['score']))
        try:
            artistmatches = match['comparison']['result']['artists']['@attr']['matches']
            jsonartists = match['comparison']['result']['artists']['artist']
            artists = []
            for artist in jsonartists:
                artists.append(artist['name'])
            artists = ", ".join(artists)
        except:
            artists = "none"
            artistmatches = "0"

        e.output = "Matching %s and %s :: Score: %s - Artists (%s matches): %s" % (user1, user2, score, artistmatches, artists)

    return e
compare.command = "!compare"
compare.helptext = """Usage: !compare <last.fm user/IRC nick> or !compare <last.fm username/IRC nick #1> <last.fm username/IRC nick #2>
Example: !compare jbieber jeffers
Compares your last.fm musical tastes with another user. A single argument compares your !setlastfm user with the specified user, 2 arguments compares the specified users."""
