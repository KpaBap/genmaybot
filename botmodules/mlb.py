import datetime, urllib.request
import xml.etree.ElementTree as ET

def mlb_schedule(self, e):
    team = e.input
    preUrl = 'http://wap.mlb.com/gdcross/components/game/mlb/year_' + datetime.date.today().strftime("%Y/month_%m/day_%d")
    activeGameUrl = preUrl + '/linescore.xml'
    masterScoreboardUrl = preUrl + '/master_scoreboard.xml'
    # url = 'http://wap.mlb.com/gdcross/components/game/mlb/year_2014/month_03/day_01/master_scoreboard.xml'
    activeGame = {}
    games = ET.parse(urllib.request.urlopen(masterScoreboardUrl)).getroot().getchildren()
    game_details = []

    def isCareAbout(team):
        truth = False

        items = [
            'ATL',
            'CLE',
            'NYY',
            'NYM',
            'BOS',
            'BAL',
            'OAK',
            'SF',
            'LAD'
        ]

        if team in items:
                truth = True

        return truth

    for game in games:
        # get results for final game specified
        if team and (team.lower() == game.attrib['home_name_abbrev'].lower() or team.lower() == game.attrib['away_name_abbrev'].lower()) and game[00].attrib['status'] != 'Final' and game[00].attrib['status'] != 'Game Over':
            activeGame = ET.parse(urllib.request.urlopen(preUrl + '/gid_' + game.attrib['gameday'] + '/miniscoreboard.xml')).getroot().getchildren()
            game_details.append('{} {} vs {} ({}-{}) {} {} | {}-{}, {} Outs P: {} AB: {} |{}Last Play: {}'.format(
                activeGame[0].attrib['delay_reason'],
                game.attrib['away_name_abbrev'],
                game.attrib['home_name_abbrev'],
                (game[1][9].attrib['away'] or 0) if game[1]._children.__len__() >= 10 else '0',
                (game[1][9].attrib['home'] or 0)  if game[1]._children.__len__() >= 10 else '0',
                activeGame[0].attrib['inning_state'],#game[00].attrib['ind'],
                game[00].attrib['inning'],
                activeGame[0].attrib['b'],
                activeGame[0].attrib['s'],
                activeGame[0].attrib['o'],

                activeGame[2][1].attrib['last'],
                activeGame[2][0].attrib['last'],
                (' Runners on: ' + (('First' if activeGame[2][8].attrib['id'] else '') + ('Second' if activeGame[2][9].attrib['id'] else ' ') + ('Third' if activeGame[2][10].attrib['id'] else ''))) if (('First' if activeGame[2][8].attrib['id'] else '') + ('Second' if activeGame[2][9].attrib['id'] else '') + ('Third' if activeGame[2][10].attrib['id'] else '')) else ' ',
                activeGame[2].attrib['last_pbp']
            ))

        elif team.lower() and (team == game.attrib['home_name_abbrev'].lower() or team == game.attrib['away_name_abbrev'].lower()) and game[00].attrib['status'] == 'Final':
            game_details.append('{} vs {} {}-{} {}/{} | WP: {} ({}-{}) {} ERA | LP: {} ({}-{}) {} ERA | SV: {} ({}-{}) {}'.format(
                game.attrib['away_name_abbrev'],
                game.attrib['home_name_abbrev'],
                game[1][9].attrib['away'] if game[1]._children.__len__() >= 10 else '0',
                game[1][9].attrib['home'] if game[1]._children.__len__() >= 10 else '0',
                game[00].attrib['ind'],
                game[00].attrib['inning'],
                game[3].attrib['last'],
                game[3].attrib['wins'],
                game[3].attrib['losses'],
                game[3].attrib['era'],
                game[4].attrib['last'],
                game[4].attrib['wins'],
                game[4].attrib['losses'],
                game[4].attrib['era'],
                game[5].attrib['last'],
                game[5].attrib['saves'],
                game[5].attrib['svo'],
                game[5].attrib['era']
            ))
        elif not team:
            if game[00].attrib['status'] == 'Final' or game[00].attrib['status'] == 'In Progress'  and (isCareAbout(game.attrib['home_name_abbrev']) or isCareAbout(game.attrib['away_name_abbrev'])):
                game_details.append('{} at {} {}-{} {}/{}'.format(
                    game.attrib['away_name_abbrev'],
                    game.attrib['home_name_abbrev'],
                    game[1][9].attrib['away'] if game[1]._children.__len__() >= 10 else '0',
                    game[1][9].attrib['home'] if game[1]._children.__len__() >= 10 else '0',
                    game[00].attrib['ind'],
                    game[00].attrib['inning']
                ))
            elif (isCareAbout(game.attrib['home_name_abbrev']) or isCareAbout(game.attrib['away_name_abbrev'])):
                game_details.append(game.attrib['away_name_abbrev'] + ' at ' + game.attrib['home_name_abbrev'] + ' ' + game.attrib['home_time'] + ' ' + game.attrib['ampm'] + ' ' + game.attrib['home_time_zone'])

    # self.logger.debug(game_details)
    e.output = ' | '.join(game_details)

    return e

mlb_schedule.command = '!mlb'
#mlb_schedule({}, {})