"""Very basic version of seen for now, doesn't notice user joins/parts/nick changes yet"""
import sqlite3
import datetime


def __init__(self):
    conn = sqlite3.connect('seen.sqlite')
    c = conn.cursor()
    result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='seen';").fetchone()
    if not result:
        c.execute('create table seen('
                  'nick text UNIQUE ON CONFLICT REPLACE, '
                  'lastline text, '
                  'channel text, '
                  'ts NOT NULL default CURRENT_TIMESTAMP)')

    result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mentions';").fetchone()
    if not result:
        c.execute('create table mentions('
                  'mentioned text UNIQUE ON CONFLICT REPLACE, '
                  'mentioner text, '
                  'line text, '
                  'channel text, '
                  'ts NOT NULL default CURRENT_TIMESTAMP)')

    conn.commit()
    c.close()


def seenlineparser(self, e):
    #we only want things said in channels
    if "#" in e.source:
        conn = sqlite3.connect('seen.sqlite')
        c = conn.cursor()
        c.execute("INSERT INTO seen(nick, lastline, channel) VALUES (?,?,?)", (e.nick.lower(), e.input, e.source))

        result = c.execute("SELECT nick FROM seen").fetchall()
        for nick in result:
            if nick[0].lower() in e.input.lower() and "!whopaged" not in e.input.lower():
                #self.logger.debug(nick[0])
                c.execute("INSERT INTO mentions (mentioned, mentioner, line, channel) "
                          "VALUES (?,?,?,?)", (nick[0], e.nick.lower(), e.input, e.source))

        conn.commit()
        c.close()
seenlineparser.lineparser = True


#Eventually I want to update this to also watch for joins/parts nick changes, etc.
def seen(self, e):
    if e.input.lower() == e.nick.lower():
        e.output = "Only you can find yourself."
    elif e.input.lower() == e.botnick.lower():
        e.output = "I'm right here."
    elif " " in e.input:
        e.output = "1 nick only! no spaming -.-"
    else:
        conn = sqlite3.connect('seen.sqlite')
        c = conn.cursor()
        if e.input != "*":
            result = c.execute("SELECT nick, lastline, channel, ts FROM "
                               "seen WHERE lower(nick) = lower(?) ORDER BY ts DESC LIMIT 1", [e.input]).fetchone()
        else:
            result = c.execute("SELECT nick, lastline, channel, ts FROM "
                               "seen WHERE lower(nick) != lower(?) ORDER BY ts DESC LIMIT 1", [e.nick]).fetchone()
        if result:
            ago = datetime.datetime.utcnow() - datetime.datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S")
            ago = self.tools['prettytimedelta'](ago)
            if not ago:
                ago = "just now"
            else:
                ago += " ago"
            e.output = '{} was last seen saying: "{}" in {} {}'.format(result[0], result[1], result[2], ago)
        else:
            e.output = "I have never seen this {} person you speak of".format(e.input)

        c.close()
    return e

seen.command = "!seen"
seen.helptext = """\
Usage: !seen <nick>
Example: !seen jeffers
Shows the last line the <nick> said and how long ago"""


def whomentioned(self, e):
    if not e.input:
        e.input = e.nick

    conn = sqlite3.connect('seen.sqlite')
    c = conn.cursor()
    result = c.execute("SELECT mentioner, line, channel, ts FROM "
                       "mentions WHERE lower(mentioned) == lower(?)  ORDER BY ts DESC LIMIT 1", [e.input]).fetchone()
    if result:
        ago = datetime.datetime.utcnow() - datetime.datetime.strptime(result[3], "%Y-%m-%d %H:%M:%S")
        ago = self.tools['prettytimedelta'](ago)
        if not ago:
            ago = "just now"
        else:
            ago += " ago"
        e.output = '{} :: <{}> {} in {}'.format(ago, result[0], result[1], result[2])
    else:
        e.output = "No one has mentioned {}".format(e.input)

    c.close()
    e.source = e.nick
    e.notice = True
    return e
whomentioned.command = "!whopaged"
whomentioned.helptext = """\
Usage: !whopaged [Optional nick]
Example: !whopaged jeffers
Shows the last line where someone mentioned the given name. If nick isn't supplied it checks your nick."""
