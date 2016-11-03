import re
import sqlite3
import urllib.request
import json
import datetime
import time
import cherrypy, threading
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class webServer:
    def __init__(self, strava_client_secret,
                 strava_client_id):  # Get the strava client ID/secrets for the Oauth exchange later
        self.strava_client_secret = strava_client_secret
        self.strava_client_id = strava_client_id

    @cherrypy.expose
    def strava_token_exchange(self, state=None, code=None, error=None):
        if code and state:
            params = urllib.parse.urlencode(
                {'client_id': self.strava_client_id, 'client_secret': self.strava_client_secret, 'code': code})
            params = params.encode('utf-8')

            req = urllib.request.Request("https://www.strava.com/oauth/token")
            req.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8")
            # pdb.set_trace()
            try:
                response = urllib.request.urlopen(req, params)
                response = json.loads(response.read().decode('utf-8'))

                self.strava_insert_token(state, response['access_token'])

                return "Strava token exchange completed successfully. You can close this window now."
            except:
                return "Token exchange with Strava failed. Please try to authenticate again."


        elif (error != None) or (code == None):
            return "Invalid or empty access code received from Strava. Please try to authenticate again."

    def strava_insert_token(self, user, token):
        """ Insert a user's strava token into the token table """
        conn = sqlite3.connect('strava.sqlite')
        c = conn.cursor()
        query = "INSERT INTO tokens VALUES (:user, :token)"
        c.execute(query, {'user': user, 'token': token})
        conn.commit()
        c.close()


# End Web server stuff
def check_strava_token(token):
    url = "https://www.strava.com/api/v3/athlete"

    try:
        headers = {'Authorization': 'Bearer ' + token}
        req = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(req)
        response = json.loads(response.read().decode('utf-8'))
        return True
    except:
        return False


def strava_get_token(user):
    """ Get an token by user """
    conn = sqlite3.connect('strava.sqlite')
    c = conn.cursor()
    query = "SELECT token FROM tokens WHERE user= :user"

    try:
        result = c.execute(query, {'user': user}).fetchone()
    except:
        return False
    if (result):
        c.close()
        return result[0]
    else:
        c.close()
        return False


def strava_oauth_exchange(self, e):
    strava_client_secret = self.botconfig["APIkeys"]["stravaClientSecret"]
    strava_client_id = self.botconfig["APIkeys"]["stravaClientId"]

    nick = e.nick
    # Send the user off to Strava to authorize us
    strava_oauth_url = "https://www.strava.com/oauth/authorize?client_id=%s&response_type=code&redirect_uri=http://%s:%s/strava/strava_token_exchange&scope=view_private&approval_prompt=auto&state=%s" % (
    strava_client_id, self.strava_web_host, self.strava_web_port, nick)
    self.irccontext.privmsg(e.nick, "Load this URL in your web browser and authorize the bot:")
    self.irccontext.privmsg(e.nick, strava_oauth_url)
    e.output = "Check your PM for further info to complete the auth process."
    return e


# this is only needed if we ever have to change the strava token
def set_stravatoken(line, nick, self, c):
    self.botconfig["APIkeys"]["stravaToken"] = line[12:]
    with open('genmaybot.cfg', 'w') as configfile:
        self.botconfig.write(configfile)


set_stravatoken.admincommand = "stravatoken"


def set_stravaclientid(line, nick, self, c):
    self.botconfig["APIkeys"]["stravaClientId"] = line[15:]
    with open('genmaybot.cfg', 'w') as configfile:
        self.botconfig.write(configfile)


set_stravaclientid.admincommand = "stravaclientid"


def set_stravaclientsecret(line, nick, self, c):
    self.botconfig["APIkeys"]["stravaClientSecret"] = line[19:]
    with open('genmaybot.cfg', 'w') as configfile:
        self.botconfig.write(configfile)


set_stravaclientsecret.admincommand = "stravaclientsecret"


def __init__(self):
    """ On init, read the token to a variable, then do a system check which runs upgrades and creates tables. """
    strava_check_system()  # Check the system for tables and/or upgrades

    strava_client_secret = self.botconfig["APIkeys"]["stravaClientSecret"]
    strava_client_id = self.botconfig["APIkeys"]["stravaClientId"]
    web_port = int(self.botconfig['webui']['port'])
    self.strava_web_port = web_port
    self.strava_web_host = "znc.00id.net"

    ##Disable cherrypy logging to stdout, bind to all IPs, start in a separate thread
    cherrypy.engine.autoreload.on = True
    cherrypy.log.screen = False
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': web_port})
    cherrypy.tree.mount(webServer(strava_client_secret, strava_client_id), "/strava")

    # wait a little bit for other instances to finish starting
    time.sleep(1.5)
    if not cherrypy.server.running:
        thread = threading.Thread(target=cherrypy.server.start, )
        thread.start()


def request_json(url):
    if not request_json.token:  # if we haven't found a valid client token, fall back to the public one
        request_json.token = self.botconfig["APIkeys"]["stravaToken"]

    headers = {'Authorization': 'access_token ' + request_json.token}
    # print ("Strava: requesting %s Headers: %s" % (url, headers))
    req = urllib.request.Request(url, None, headers)
    response = urllib.request.urlopen(req)
    response = json.loads(response.read().decode('utf-8'))
    return response


def strava_software_version():
    """ Returns the current version of the strava module, used upgrade """
    return 1


def strava_check_system():
    """ Run upgrades and check on initial table creation/installation """
    strava_check_upgrades()
    strava_check_create_tables()


def strava_check_upgrades():
    """ Check the version in the database and upgrade the system recursively until we're at the current version """
    software_version = strava_get_version('software')
    latest_version = strava_software_version()
    if (software_version == False):
        # This must be a new revision
        # we need to set it to the current version that is being installed.
        strava_set_version('software', latest_version)
        strava_check_upgrades()
    elif (software_version < strava_software_version()):
        # Then we need to perform an upgrade for this version.
        func = 'strava_upgrade_%s' % (software_version + 1)
        globals()[func]()
        strava_check_upgrades()


def strava_set_version(version_field, version_number):
    """ Sets a version number for any component """
    conn = sqlite3.connect('strava.sqlite')
    c = conn.cursor()
    query = "INSERT INTO version VALUES (:version_field, :version_number)"
    c.execute(query,
              {'version_field': version_field,
               'version_number': version_number})
    conn.commit()
    c.close()


def strava_get_version(version_field):
    """ Get the version for a component of code """
    strava_check_create_tables()
    conn = sqlite3.connect('strava.sqlite')
    c = conn.cursor()
    query = "SELECT version_number FROM version WHERE version_field = :version_field"
    result = c.execute(query, {'version_field': version_field}).fetchone()
    if (result):
        c.close()
        return result[0]
    else:
        c.close()
        return False


def strava_check_create_tables():
    """ Create tables for the database, these should always be up to date """
    conn = sqlite3.connect('strava.sqlite')
    c = conn.cursor()
    tables = {
        'version': "CREATE TABLE version (version_field TEXT, version_number INTEGER)",
        'athletes': "CREATE TABLE athletes (user TEXT UNIQUE ON CONFLICT REPLACE, strava_id TEXT)"
    }
    # Go through each table and check if it exists, if it doesn't, run the SQL statement to create it.
    for (table_name, sql_statement) in tables.items():
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"
        if not c.execute(query, {'table_name': table_name}).fetchone():
            # Run the command.
            c.execute(sql_statement)
            conn.commit()
    c.close()


def strava_insert_athlete(nick, athlete_id):
    """ Insert a user's strava id into the athletes table """
    conn = sqlite3.connect('strava.sqlite')
    c = conn.cursor()
    query = "INSERT INTO athletes VALUES (:user, :strava_id)"
    c.execute(query, {'user': nick, 'strava_id': athlete_id})
    conn.commit()
    c.close()


def strava_delete_athlete(nick, athlete_id):
    """ Delete a user's strava id from the athletestable """
    conn = sqlite3.connect('strava.sqlite')
    c = conn.cursor()
    query = "DELETE FROM athletes WHERE user = :user AND strava_id = :strava_id"
    c.execute(query, {'user': nick, 'strava_id': athlete_id})
    conn.commit()
    c.close()


def strava_get_athlete(nick):
    """ Get an athlete ID by user """
    conn = sqlite3.connect('strava.sqlite')
    c = conn.cursor()
    query = "SELECT strava_id FROM athletes WHERE UPPER(user) = UPPER(?)"
    result = c.execute(query, [nick]).fetchone()
    if (result):
        c.close()
        return result[0]
    else:
        c.close()
        return False


def strava_line_parser(self, e):
    """ Watch every line for a valid strava line """
    url = re.search(
        r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>])*\))+(?:\(([^\s()<>])*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",
        e.input)
    if url:
        url = url.group(0)
        url_parts = urlparse(url)
        if url_parts[1] == 'www.strava.com' or url_parts[1] == 'app.strava.com':
            ride = re.match(r"^/activities/(\d+)", url_parts[2])
            if ride and ride.group(1):
                recent_ride = strava_get_ride_extended_info(ride.group(1))
                if recent_ride:
                    e.output = strava_ride_to_string(recent_ride)
                else:
                    e.output = "Sorry %s, an error has occured attempting to retrieve ride details for %s. They said Ruby was webscale..." % (
                    e.nick, url)
                return e
    else:
        return


strava_line_parser.lineparser = False


def strava_set_athlete(self, e):
    """ Set an athlete's Strava ID. """
    if e.input.isdigit():
        # Insert the user strava id, we should probably validate the user though right?
        if (strava_is_valid_user(e.input)):
            strava_insert_athlete(e.nick, e.input)
            self.irccontext.privmsg(e.nick, "Your Strava ID has been set to %s. Now go play bikes." % (e.input))
        else:
            # Inform the user that the strava id isn't valid.
            self.irccontext.privmsg(e.nick, "Sorry, that is not a valid Strava user.")
    else:
        # Bark at stupid users.
        self.irccontext.privmsg(e.nick, "Usage: !strava set <strava id>")


# strava_set_athlete.command = "!strava-set"
# strava_set_athlete.helptext = """
#                        Usage: !strava-set <strava id>
#                        Example: !strava-set 12345
#                        Saves your Strava ID to the bot.
#                        Once your Strava ID is saved you can use those commands without an argument."""


def strava_reset_athlete(self, e):
    """ Resets an athlete's Strava ID. """
    athlete_id = strava_get_athlete(e.nick)
    if athlete_id:
        strava_delete_athlete(e.nick, athlete_id)
        self.irccontext.privmsg(e.nick,
                                "Your Strava ID has been reset, but remember, if it's not on Strava, it didn't happen.")
    else:
        self.irccontext.privmsg(e.nick, "You don't even have a Strava ID set, why would you want to reset it?")


# strava_reset_athlete.command = "!strava-reset"
# strava_reset_athlete.helptext = """
#                        Usage: !strava-reset
#                        Removes your Strava ID from the bot."""


def strava(self, e):
    strava_id = strava_get_athlete(e.nick)
    # set the token for the current user
    token = strava_get_token(e.nick)

    if check_strava_token(token):
        request_json.token = token
    else:
        request_json.token = self.botconfig["APIkeys"]["stravaToken"]

    if e.input.isdigit():
        try:
            if strava_is_valid_user(e.input):
                # Process a last ride request for a specific strava id.
                rides_response = request_json("https://www.strava.com/api/v3/athletes/%s/activities" % e.input)
                e.output = strava_extract_latest_ride(rides_response, e, e.input)
            else:
                e.output = "Sorry, that is not a valid Strava user."
        except urllib.error.URLError:
            e.output = "Unable to retrieve rides from Strava ID: %s. The user may need to do: !strava auth" % (e.input)
    elif e.input:
        athlete_id = strava_get_athlete(e.input)
        # set the token for the provided user, if we have it
        token = strava_get_token(e.input)

        if check_strava_token(token):
            request_json.token = token
        else:
            request_json.token = self.botconfig["APIkeys"]["stravaToken"]

        if athlete_id:
            try:
                if strava_is_valid_user(athlete_id):
                    # Process a last ride request for a specific strava id.
                    rides_response = request_json("https://www.strava.com/api/v3/athletes/%s/activities" % athlete_id)
                    e.output = strava_extract_latest_ride(rides_response, e, athlete_id)
                else:
                    e.output = "Sorry, that is not a valid Strava user."
            except urllib.error.URLError:
                e.output = "Unable to retrieve rides from Strava ID: %s. The user may need to do: !strava auth" % (
                athlete_id)
        else:
            # We still have some sort of string, but it isn't numberic.
            e.output = "Sorry, %s is not a valid Strava ID." % (e.input)
    elif strava_id:
        try:
            if strava_is_valid_user(strava_id):
                # Process the last ride for the current strava id.
                rides_response = request_json("https://www.strava.com/api/v3/athletes/%s/activities" % strava_id)
                e.output = strava_extract_latest_ride(rides_response, e, strava_id)
            else:
                e.output = "Sorry, that is not a valid Strava user."
        except urllib.error.URLError:
            e.output = "Unable to retrieve rides from Strava ID: %s. The user may need to do: !strava auth" % (
            strava_id)
    else:
        e.output = "Sorry %s, you don't have a Strava ID setup yet, please enter one with the !strava set [id] command. Also run !strava auth if you have Strava privacy enabled. Remember, if it's not on Strava, it didn't happen." % (
        e.nick)
    return e


# strava.command = "!strava"
# strava.helptext = """
#                        Usage: !strava [strava id]"
#                        Example: !strava-last, !strava-last 12345
#                        Gets the information about the last ride for the Strava user.
#                        If you have a Strava ID set with !strava-set you can use this command without an arguement.
#                        """


def strava_achievements(self, e):
    # beardedw1zard
    if not e.input:
        e.output += strava_achievements.helptext
        return e
    # end beardedw1zard
    """ Get Achievements for a ride. """
    strava_id = strava_get_athlete(e.nick)
    # set the token for the current user
    token = strava_get_token(e.nick)

    if check_strava_token(token):
        request_json.token = token
    else:
        request_json.token = self.botconfig["APIkeys"]["stravaToken"]

    if e.input.isdigit():
        ride_info = strava_get_ride_extended_info(e.input)
        if ride_info:
            achievements = strava_get_ride_achievements(e.input)
            if achievements:
                e.output = "Achievements for %s: %s" % (ride_info['name'], ', '.join(achievements))
            else:
                e.output = "There were no achievements on %s, time to harden the fuck up." % (ride_info['name'])
        else:
            e.output = "Sorry, that is an invalid Strava Ride ID."
    elif e.input:
        athlete_id = strava_get_athlete(e.input)
        # set the token for the provided user, if we have it
        token = strava_get_token(e.input)

        if check_strava_token(token):
            request_json.token = token
        else:
            request_json.token = self.botconfig["APIkeys"]["stravaToken"]

        if athlete_id:
            try:
                if strava_is_valid_user(athlete_id):
                    # Process the last ride for the current strava id.
                    response = urllib.request.urlopen('http://app.strava.com/api/v1/rides?athleteId=%s' % (athlete_id))
                    rides_response = json.loads(response.read().decode('utf-8'))
                    if 'rides' in rides_response:
                        recent_ride = rides_response['rides'][0]
                        achievements = strava_get_ride_achievements(recent_ride['id'])
                        if achievements:
                            e.output = "Achievements for %s: %s" % (recent_ride['name'], ', '.join(achievements))
                        else:
                            e.output = "There were no achievements on %s, time to harden the fuck up." % (
                            recent_ride['name'])
                    else:
                        e.output = "%s does not have any recent achievements." % (e.input)
                else:
                    e.output = "The Strava ID setup for %s is invalid." % (e.input)
            except urllib.error.URLError:
                e.output = "Unable to retrieve rides from Strava ID: %s. The user may need to do: !strava auth" % (
                e.input)
        else:
            e.output = "%s does not have a valid Strava ID setup. Remember, if it's not on Strava, it didn't happen." % (
            e.input)
    elif strava_id:
        try:
            if strava_is_valid_user(strava_id):
                # Process the last ride for the current strava id.
                response = urllib.request.urlopen('http://app.strava.com/api/v1/rides?athleteId=%s' % (strava_id))
                rides_response = json.loads(response.read().decode('utf-8'))
                if 'rides' in rides_response:
                    recent_ride = rides_response['rides'][0]
                    achievements = strava_get_ride_achievements(recent_ride['id'])
                    if achievements:
                        e.output = "Achievements for %s: %s" % (recent_ride['name'], ', '.join(achievements))
                    else:
                        e.output = "There were no achievements on %s, time to harden the fuck up." % (
                        recent_ride['name'])
                else:
                    e.output = "You do not have any recent achievements."
            else:
                e.output = "You do not have a valid Strava ID setup."
        except urllib.error.URLError:
            e.output = "Unable to retrieve rides from Strava ID: %s The user may need to do: !strava auth" % (e.input)
    else:
        e.output = "Sorry %s, you don't have a Strava ID setup yet, please enter one with the !strava set [id] command. Also run !strava auth if you have Strava privacy enabled. Remember, if it's not on Strava, it didn't happen." % (
        e.nick)
    return e


# strava_achievements.command = "!strava-achievements"
strava_achievements.helptext = """Usage: !strava-achievements [ride id]. Gets the achievements for a Ride ID"""


# ==== begin beardedwizard
def strava_parent(self, e):
    strava_command_handler(self, e)
    return e


strava_parent.command = "!strava"
strava_parent.helptext = "Fetch last ride: \"!strava [optional nick]\", Set your ID: \"!strava set <athelete id>\", Reset your ID: \"!strava reset\", List achievements for a ride: \"!strava achievements <ride id>\", Allow the bot to read your private rides: \"!strava auth\""


def strava_help(self, e):
    e.output += strava_parent.helptext
    return e


def strava_command_handler(self, e):
    arg_offset = 0
    val_offset = 1
    function = None

    arg_function_dict = {'auth': strava_oauth_exchange, 'get': strava, 'set': strava_set_athlete,
                         'reset': strava_reset_athlete, 'achievements': strava_achievements, 'help': strava_help}
    arg_list = list(arg_function_dict.keys())

    # EX: "set 123456"
    words = e.input.split()

    # There is something in input
    # EX: "achievements 12345"
    if (arg_is_present(words)):
        if (is_known_arg(words, arg_list)):
            # Always clean the arg even if no value is present, patch strava* functions to handle None for e.input
            # EX: "12345" or None
            e.input = clean_arg_from_input(e.input)

        try:
            function = arg_function_dict[words[arg_offset]]
            print(
            "Calling " + function.__name__ + " with e.input of: " + ''.join('none' if e.input is None else e.input))
            function(self, e)
            return e
        except KeyError:
            pass

    # There are no args or only unknown args. We fall through from the exception above
    # EX: "" or "beardedw1zard"
    function = arg_function_dict['get']
    print("Calling " + function.__name__ + " with e.input of: " + ''.join('none' if e.input is None else e.input))
    function(self, e)

    return e


def arg_is_present(words):
    return len(words)


def is_known_arg(args, known_args):
    results = [arg for arg in args if arg in known_args]
    if (len(results)):
        return 1
    return 0


def clean_arg_from_input(string):
    if (len(string.split()) > 1):
        print("returning: " + ' '.join(string.split()[1:]))
        return ' '.join(string.split()[1:])
    return


# ==== end beardedwizard

def strava_extract_latest_ride(response, e, athlete_id=None):
    """ Grab the latest ride from a list of rides and gather some statistics about it """
    if response:
        recent_ride = response[0]
        recent_ride = strava_get_ride_extended_info(recent_ride['id'])
        if recent_ride:
            return strava_ride_to_string(recent_ride, athlete_id)
        else:
            return "Sorry %s, an error has occured attempting to retrieve the most recent ride's details. They said Ruby was webscale..." % (
            e.nick)
    else:
        return "Sorry %s, no rides have been recorded yet. You may need to run '!strava auth' Remember, if it's not on Strava, it didn't happen." % (
        e.nick)


def strava_ride_to_string(recent_ride, athlete_id=None):  # if the athlete ID is missing we can default to mph
    # Convert a lot of stuff we need to display the message
    moving_time = str(datetime.timedelta(seconds=recent_ride['moving_time']))
    ride_datetime = time.strptime(recent_ride['start_date_local'], "%Y-%m-%dT%H:%M:%SZ")
    time_start = time.strftime("%B %d, %Y at %I:%M %p", ride_datetime)

    # Try to get the average heart rate
    if 'average_heartrate' in recent_ride:
        avg_hr = recent_ride['average_heartrate']
    else:  # Heart not found
        avg_hr = False

    if athlete_id:
        measurement_pref = strava_get_measurement_pref(athlete_id)
    else:
        measurement_pref = None

    if measurement_pref == "feet" or athlete_id == None or measurement_pref == None:

        mph = strava_convert_meters_per_second_to_miles_per_hour(recent_ride['average_speed'])
        mph = str(mph)
        mph = mph.replace('.', '/')
        miles = strava_convert_meters_to_miles(recent_ride['distance'])
        miles = int(miles)
        max_mph = strava_convert_meters_per_second_to_miles_per_hour(recent_ride['max_speed'])
        feet_climbed = strava_convert_meters_to_feet(recent_ride['total_elevation_gain'])
        # Output string
        #         return_string = "%s on %s (http://www.strava.com/activities/%s)\n" % (recent_ride['name'], time_start, recent_ride['id'])
        #         return_string += "Ride Stats: %s mi in %s | %s mph average / %s mph max | %s feet climbed" % (miles, moving_time, mph, max_mph, int(feet_climbed))
        return_string = "%s@%s" % (miles, mph)

    elif measurement_pref == "meters":
        kmh = round(float(recent_ride['average_speed']) * 3.6, 1)  # meters per second to km/h
        kmh = str(kmh)
        kmh = kmh.replace('.', '/')
        km = round(float(recent_ride['distance'] / 1000), 1)  # meters to km
        km = int(km)
        max_kmh = round(float(recent_ride['max_speed']) * 3.6, 1)  # m/s to km/h
        m_climbed = recent_ride['total_elevation_gain']
        #         return_string = "%s on %s (http://www.strava.com/activities/%s)\n" % (recent_ride['name'], time_start, recent_ride['id'])
        #         return_string += "Ride Stats: %s km in %s | %s km/h average / %s km/h max | %s meters climbed" % (km, moving_time, kmh, max_kmh, int(m_climbed))
        return_string = "%s@%s" % (km, kmh)


        # Figure out if we need to add average watts to the string.
        # Users who don't have a weight won't have average watts.
    #     if 'average_watts' in recent_ride:
    #         return_string += " | %s watts average power" % (int(recent_ride['average_watts']))
    #         if avg_hr > 0: 
    #             return_string += " | %s watts/bpm" % (round(recent_ride['average_watts']/avg_hr,2))
    return return_string


def strava_get_measurement_pref(athlete_id):
    try:
        athlete_info = request_json("https://www.strava.com/api/v3/athletes/%s" % athlete_id)
        if athlete_info:
            return athlete_info['measurement_preference']
    except:
        return None


def strava_get_ride_extended_info(ride_id):
    """ Get all the details about a ride. """
    try:
        ride_details = request_json("https://www.strava.com/api/v3/activities/%s" % ride_id)
        print(ride_details)
        if ride_details:
            return ride_details
        else:
            return False
    except urllib.error.URLError:
        return False


def strava_get_ride_efforts(ride_id):
    """ Get all the efforts (segments and their respective performance) from a ride. """
    try:
        response = urllib.request.urlopen("http://www.strava.com/api/v1/rides/%s/efforts" % (ride_id))
        ride_efforts = json.loads(response.read().decode('utf-8'))
        if 'efforts' in ride_efforts:
            return ride_efforts['efforts']
        else:
            return False
    except urllib.error.URLError:
        return False


def strava_get_ride_achievements(ride_id):
    try:
        ride_achievements = list()
        response = urllib.request.urlopen("http://app.strava.com/rides/%s" % (ride_id))
        page_text = response.read().decode('utf-8')
        soup = BeautifulSoup(page_text)
        table = soup.find('table', {'class': 'top-achievements'})
        if table:
            trs = table.findAll('tr')
            if trs:
                for tr in trs:
                    tds = tr.findAll('td')
                    if tds:
                        tx = re.sub('\n', ' ', ''.join(tds[1].findAll(text=True))).strip()
                        ride_achievements.append(tx)
        return ride_achievements
    except urllib.error.URLError:
        return False


def strava_get_ride_distance_since_date(athlete_id, begin_date, offset_count=0):
    """ Recursively aggregate all of the ride mileage since the begin_date by using strava's pagination """
    try:
        ride_distance_sum = 0
        response = urllib.request.urlopen("http://app.strava.com/api/v1/rides?date=%s&athleteId=%s&offset=%s" % (
        begin_date, athlete_id, offset_count))
        rides_details = json.loads(response.read().decode('utf-8'))
        if 'rides' in rides_details:
            for ride in rides_details['rides']:
                ride_details = strava_get_ride_extended_info(ride['id'])
                if 'distance' in ride_details:
                    ride_distance_sum = ride_distance_sum + strava_convert_meters_to_miles(ride_details['distance'])
            ride_distance_sum = ride_distance_sum + strava_get_ride_distance_since_date(athlete_id, begin_date,
                                                                                        offset_count + 50)
        else:
            return ride_distance_sum
    except urllib.error.URLError:
        return 0


def strava_is_valid_user(strava_id):
    """ Checks to see if a strava id is a valid strava user """
    try:
        response = urllib.request.urlopen("http://app.strava.com/athletes/%s" % (strava_id))
        if response:
            return True
        else:
            return False
    except urllib.error.URLError:
        return False


def strava_convert_meters_per_second_to_miles_per_hour(mps):
    """ Converts meters per second to miles per hour, who the fuck uses this to measure bike speed? Idiots. """
    mph = 2.23694 * float(mps)
    return round(mph, 1)


def strava_convert_meters_per_hour_to_miles_per_hour(meph):
    """ Convert meters per hour to miles per hour. """
    mph = 0.000621371192 * float(meph)
    return round(mph, 1)


def strava_convert_meters_to_miles(meters):
    """ Convert meters to miles. """
    miles = 0.000621371 * float(meters)
    return round(miles, 1)


def strava_convert_meters_to_feet(meters):
    """ Convert meters to feet. """
    feet = 3.28084 * float(meters)
    return round(feet, 1)
