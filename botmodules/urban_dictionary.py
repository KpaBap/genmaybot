import urllib.parse
import re
import html


def get_urbandictionary(self, e):
    searchterm = e.input
    
    #super smrt AI code to tell if you want a different definition
    #We only get the first 7 results.
    number = re.search("-[1-7]", searchterm[0:2])
    if number and len(searchterm.split(" ")) > 1:
       searchterm = searchterm[3:]
       number = int(number.group(0)[1:2]) - 1
       self.logger.debug(number)
    else:
       number = 0

    url = "http://www.urbandictionary.com/define.php?term=%s" % urllib.parse.quote(searchterm)

    if searchterm == "wotd":
        e.output = get_urbandictionary_wotd(self)
        return e

    if searchterm == "":
        url = "http://www.urbandictionary.com/random.php"

    page, url = self.tools["load_html_from_url"](url, returnurl=True)

    first_definition = ""

    if page.find(id='not_defined_yet') is not None:
        return None

    first_word = page.findAll('a', attrs={"class": "word"})[number].string

    first_word = first_word.replace("\n", "")

    for content in page.findAll('div', attrs={"class": "meaning"})[number].contents:
        if content.string is not None:
            first_definition += content.string


    first_definition = first_definition.replace("\n", " ")
    first_definition = first_definition.replace("\r", " ")
    first_definition = first_definition[0:392]

    first_word = html.unescape(first_word)
    first_definition = html.unescape(first_definition)
    
    first_definition = first_word + ": " + first_definition + " [ %s ]" % self.tools['shorten_url'](url)

    e.output = first_definition
    return e

get_urbandictionary.command = "!ud"
get_urbandictionary.helptext = """Usage: !ud <word or phrase>
Example: !ud hella
Shows urbandictionary definition of a word or phrase.
!ud alone returns a random entry
!ud wotd returns the current word of the day"""


def get_urbandictionary_wotd(self):

    url = "http://www.urbandictionary.com"
    page = self.tools["load_html_from_url"](url)
    first_definition = ""

    first_word = page.findAll('a', attrs={"class": "word"})[0].string
    first_word = first_word.encode("utf-8", 'ignore')

    for content in page.findAll('div', attrs={"class": "meaning"})[0].contents:
        if content.string is not None:
            first_definition += content.string

    first_definition = first_definition.replace("\n", " ")
    
    first_word = html.unescape(first_word)
    first_definition = html.unescape(first_definition)
    
    wotd = first_word.decode('utf-8') + ": " + first_definition + " [ %s ]" % self.tools['shorten_url'](url)

    return wotd
