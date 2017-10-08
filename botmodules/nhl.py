import json
import urllib.request
import datetime
import pytz

ET = pytz.timezone("US/Eastern")

def get_nhl_games(self, e):
    if e.input:
        today = e.input
    else:
        today = datetime.date.today().strftime("%Y-%m-%d")
        
    url = "http://statsapi.web.nhl.com/api/v1/schedule?startDate={0}&endDate={0}&expand=schedule.teams,schedule.linescore".format(today)
    data = urllib.request.urlopen(url).read().decode()
    data = json.loads(data)
    data = data['dates'][0]
         
    games = []
    for game in data['games']:
 
        if game['status']['statusCode'] is "1":
            # game is scheduled in future
            starttime = datetime.datetime.strptime(game['gameDate'], "%Y-%m-%dT%H:%M:%SZ")
            starttime = starttime.replace(tzinfo=pytz.utc).astimezone(tz=ET)
            starttime = starttime.strftime('%I:%M%p').lstrip('0').replace(':00', '')

            gametxt = "{} @ {} ({} ET)".format(game['teams']['away']['team']['teamName'],
        	                                   game['teams']['home']['team']['teamName'],
        	                                   starttime)
        else:
            # game finished or currently on
            away = '{} {}'.format(game['teams']['away']['team']['teamName'],
            	                  game['linescore']['teams']['away']['goals'])
            
            home = '{} {}'.format(game['linescore']['teams']['home']['goals'],
            	                  game['teams']['home']['team']['teamName'])
            	                  
            status = '{} {}'.format(game['linescore']['currentPeriodTimeRemaining'],
            	                    game['linescore']['currentPeriodOrdinal'])
            	                    
            if game['status']['statusCode'] is "7":
                status = status.replace("3rd", "").strip()
                
            gametxt = "{} - {} ({})".format(away, home, status)
            
        games.append(gametxt)
        
    e.output = " | ".join(games)
    return e
        
get_nhl_games.command = "!nhl"

#get_nhl_games.input = "2017-10-07"
#get_nhl_games(None,  get_nhl_games)
#print(get_nhl_games.output)
