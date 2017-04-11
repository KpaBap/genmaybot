def get_trope(self, e, urlposted=False):

    if urlposted:
        if "tvtropes.org/pmwiki/pmwiki.php" in e.input:
            url = e.input
        else:
            return
    elif not e.input:
        url = "http://tvtropes.org/pmwiki/randomitem.php?p=1"
    else:
        searchterm = "site:tvtropes.org " + e.input
        url = self.tools['google_url'](searchterm, "tvtropes.org/pmwiki/pmwiki.php")

    page, url = self.tools["load_html_from_url"](url, returnurl=True)

    pagetitle = page.find("div", {"class": "pagetitle"}).span.string
    page = page.select('#wikitext')[0].extract()
    for div in page.findAll('div'):
        div.extract()

    trope = self.tools['remove_html_tags'](str(page))

    trope = trope.replace("\n", " ").strip()

    trope = "{}: {}".format(pagetitle, trope[0:392])
    if trope.rfind(".") != -1:
        trope = trope[0:trope.rfind(".") + 1]

    if not urlposted:
        trope = trope + " [ %s ]" % self.tools['shorten_url'](url)

    e.output = trope
    return e

get_trope.command = "!trope"
