import datetime, urllib.request
import json

def get_nhl_live_games(self, e, web_call=False):
    if e.input:
        today = e.input
    else:
        today = datetime.date.today().strftime("%Y-%m-%d")
    url = "http://live.nhle.com/GameData/GCScoreboard/{}.jsonp".format(today)
    request = urllib.request.urlopen(url)
    data = request.read().decode()[15:-2]
    data = json.loads(data)

    games = []
    for game in data['games']:
        if not game['bsc']:
            start = game['bs'].replace(':00 ', ' ')
            gametxt = "{} - {} ({} ET)".format(game['atcommon'].title(),
                                               game['htcommon'].title(),
                                               start)
        else:
            gametxt = "{} {} - {} {} ({})".format(game['atcommon'].title(),
                                                  game['ats'],
                                                  game['hts'],
                                                  game['htcommon'].title(),
                                                  game['bs'])
        games.append(gametxt)

    if web_call:
        return " | ".join(games)

    e.output = " | ".join(games)
    return e

get_nhl_live_games.command = "!nhl"
get_nhl_live_games.helptext = "Usage: !nhl Shows today's hockey games and current scores"
get_nhl_live_games.webExposed = True 
