import time


def get_unalaska_blotter(self, e):
    url = "http://kucb.org/community/blotter/"
    page = self.tools["load_html_from_url"](url)

    try:
        blots = page.findAll('div', attrs={'id': 'blots'})[0]
        first_blot = blots.findAll('div', attrs={'class': 'blot'})[0]

        headline = first_blot.findAll('span', attrs={'class': 'headline small'})[0].string
        blotdate = first_blot.findAll('span', attrs={'class': 'date'})[0].string
        details = first_blot.findAll('span', attrs={'class': 'details'})[0].string
    except:
        self.logger.debug("\nSomething went wrong with processing the blotter page in unalaska_blotter.py\n")

    #Convert date to a bit shorter format
    blotdate = blotdate.replace(".", "")
    blotdate = time.strftime("%H:%M %a %m/%d/%y", time.strptime(blotdate, "%A %d %B %Y, %I:%M %p"))

    e.output = "%s [%s] %s" % (headline, blotdate, details)
    return e

get_unalaska_blotter.command = "!blot"
get_unalaska_blotter.helptext = "Usage: !blot\n Retrieve the latest witty police blotter entry from the city of Unalaska, Alaska"
