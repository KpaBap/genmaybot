import time


def get_unalaska_blotter(self, e):
    url = "http://kucb.org/community/blotter/"
    page = self.tools["load_html_from_URL"](url)

    try:
        blots = page.findAll('div', attrs={'id': 'blots'})[0]
        firstBlot = blots.findAll('div', attrs={'class': 'blot'})[0]

        headline = firstBlot.findAll('span', attrs={'class': 'headline small'})[0].string
        blotdate = firstBlot.findAll('span', attrs={'class': 'date'})[0].string
        details = firstBlot.findAll('span', attrs={'class': 'details'})[0].string
    except:
        self.logger.debug("\nSomething went wrong with processing the blotter page in unalaska_blotter.py\n")
        pass

    #Convert date to a bit shorter format
    blotdate = blotdate.replace(".", "")
    blotdate = time.strftime("%H:%M %a %m/%d/%y", time.strptime(blotdate, "%A %d %B %Y, %I:%M %p"))

    e.output = "%s [%s] %s" % (headline, blotdate, details)
    return e

get_unalaska_blotter.command = "!blot"
get_unalaska_blotter.helptext = "Usage: !blot\n Retrieve the latest witty police blotter entry from the city of Unalaska, Alaska"
