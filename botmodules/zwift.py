import urllib.request
import xmltodict
import iso8601
import datetime
import string


def call_zwift(self, e):
    zwift = Zwift()
    current_map = zwift.current_map()
    next_map = zwift.next_map()
    time_until_next = zwift.time_until_next()

    if current_map and next_map:
        e.output = e.nick + ', the current map is ' + current_map + '. ' + next_map + ' will start in ' + zwift.timedelta_to_string(time_until_next)
    elif current_map:
        e.output = e.nick + ', the current map is ' + current_map
    elif next_map:
        e.output = e.nick + ', the next map is ' + next_map + ' in ' + zwift.timedelta_to_string(time_until_next)
    else:
        e.output = e.nick + ', I have no clue, try http://whatsonzwift.com/'

call_zwift.command = "!zwift"


class Zwift:
    map_xml = None

    def __init__(self):
        self.load_xml()

    def load_xml(self):
        map_xml = urllib.request.urlopen('http://whatsonzwift.com/MapSchedule.xml').read().decode('utf-8')
        self.map_xml = xmltodict.parse(map_xml)

    def current_map(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        latest_stamp = None
        active_map = None
        for appointment in self.map_xml['MapSchedule']['appointments']['appointment']:
            starts_at = iso8601.parse_date(appointment['@start'])
            starts_at = starts_at.astimezone(datetime.timezone.utc)
            if starts_at <= now and (latest_stamp is None or starts_at >= latest_stamp):
                active_map = appointment['@map']
                latest_stamp = starts_at
        if active_map:
            return string.capwords(active_map)
        else:
            return None

    def next_map(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        earliest_stamp = None
        next_map = None
        for appointment in self.map_xml['MapSchedule']['appointments']['appointment']:
            starts_at = iso8601.parse_date(appointment['@start'])
            if starts_at > now and (earliest_stamp is None or starts_at < earliest_stamp):
                next_map = appointment['@map']
                earliest_stamp = starts_at
        if next_map:
            return string.capwords(next_map)
        else:
            return None

    def time_until_next(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        earliest_stamp = None
        for appointment in self.map_xml['MapSchedule']['appointments']['appointment']:
            starts_at = iso8601.parse_date(appointment['@start'])
            if starts_at > now and (earliest_stamp is None or starts_at < earliest_stamp):
                earliest_stamp = starts_at
        if earliest_stamp:
            diff = earliest_stamp - now
            return diff
        else:
            return None

    def timedelta_to_string(self, timedelta):
        hours = int(timedelta.seconds / 60 / 60)
        minutes = int((timedelta.seconds / 60) - (hours * 60))
        seconds = int(timedelta.seconds - ((hours * 60 * 60) + (minutes * 60)))
        return '{} days {} hours {} minutes {} seconds'.format(
            int(timedelta.days),
            int(hours),
            int(minutes),
            int(seconds)
        )
