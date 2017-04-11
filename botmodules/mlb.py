import datetime, urllib.request
import xml.etree.ElementTree as ET

def mlb_schedule(self, e):
    team = e.input
    pre_url = 'http://wap.mlb.com/gdcross/components/game/mlb/year_' + datetime.date.today().strftime("%Y/month_%m/day_%d")
    active_game_url = pre_url + '/linescore.xml'
    master_scoreboard_url = pre_url + '/master_scoreboard.xml'

    active_game = {}
    games = ET.parse(urllib.request.urlopen(master_scoreboard_url)).getroot().getchildren()
    game_details = []

    def is_care_about(team):
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
            active_game = ET.parse(urllib.request.urlopen(pre_url + '/gid_' + game.attrib['gameday'] + '/miniscoreboard.xml')).getroot().getchildren()
            game_details.append('{} {} vs {} ({}-{}) {} {} | {}-{}, {} Outs P: {} AB: {} |{}Last Play: {}'.format(
                active_game[0].attrib['delay_reason'],
                game.attrib['away_name_abbrev'],
                game.attrib['home_name_abbrev'],
                (game[1][9].attrib['away'] or 0) if game[1]._children.__len__() >= 10 else '0',
                (game[1][9].attrib['home'] or 0)  if game[1]._children.__len__() >= 10 else '0',
                active_game[0].attrib['inning_state'],#game[00].attrib['ind'],
                game[00].attrib['inning'],
                active_game[0].attrib['b'],
                active_game[0].attrib['s'],
                active_game[0].attrib['o'],

                active_game[2][1].attrib['last'],
                active_game[2][0].attrib['last'],
                (' Runners on: ' + (('First' if active_game[2][8].attrib['id'] else '') + ('Second' if active_game[2][9].attrib['id'] else ' ') + ('Third' if active_game[2][10].attrib['id'] else ''))) if (('First' if active_game[2][8].attrib['id'] else '') + ('Second' if active_game[2][9].attrib['id'] else '') + ('Third' if active_game[2][10].attrib['id'] else '')) else ' ',
                active_game[2].attrib['last_pbp']
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
            if game[00].attrib['status'] == 'Final' or game[00].attrib['status'] == 'In Progress'  and (is_care_about(game.attrib['home_name_abbrev']) or is_care_about(game.attrib['away_name_abbrev'])):
                game_details.append('{} at {} {}-{} {}/{}'.format(
                    game.attrib['away_name_abbrev'],
                    game.attrib['home_name_abbrev'],
                    game[1][9].attrib['away'] if game[1]._children.__len__() >= 10 else '0',
                    game[1][9].attrib['home'] if game[1]._children.__len__() >= 10 else '0',
                    game[00].attrib['ind'],
                    game[00].attrib['inning']
                ))
            elif is_care_about(game.attrib['home_name_abbrev']) or is_care_about(game.attrib['away_name_abbrev']):
                game_details.append(game.attrib['away_name_abbrev'] + ' at ' + game.attrib['home_name_abbrev'] + ' ' + game.attrib['home_time'] + ' ' + game.attrib['ampm'] + ' ' + game.attrib['home_time_zone'])

    e.output = ' | '.join(game_details)

    return e

mlb_schedule.command = '!mlb'
