import re


def get_wiki(self, e, urlposted=False, forcemediawiki=False):
    #read the first paragraph of a wikipedia article
    searchterm = e.input

    if urlposted:
        url = searchterm
    else:
        if searchterm == "":
            url = "http://en.wikipedia.org/wiki/Special:Random"
        else:
            searchterm = "site:wikipedia.org " + searchterm
            url = self.tools['google_url'](searchterm, "wikipedia.org/wiki")

    title = ""

    if url and url.find("wikipedia.org/wiki/") != -1 or forcemediawiki:
        if url.find("File:") != -1:
            title = get_wiki_file_description(self, url)
        else:
            title, url = read_wiki_page(self, url)

    if not urlposted and title:
        title = title.encode('utf-8')
        url = self.tools['shorten_url'](url)

        # Shorten the title to fit perfectly in the IRC 510-character per line limit
        # To do so properly, you have to convert to utf-8 because of double-byte characters
        # The protocol garbage before the real message is
        # :<nick>!<realname>@<hostname> PRIVMSG <target> :

        maxlen = 510 - len(":{}!{}@{} PRIVMSG {} : [ {} ]".format(e.botnick,
                                                                  self.realname,
                                                                  self.hostname,
                                                                  e.source, url))
        title = title[0:maxlen]

        title = title.decode('utf-8')

        title = title + " [ %s ]" % url

    e.output = title
    return e
get_wiki.command = "!wiki"
get_wiki.helptext = """\
Usage: !wiki <search term>
Example: !wiki carl sagan
Shows the first couple of sentences of a wikipedia entry for the given search term"""""


def read_wiki_page(self, url):
    page, url = self.tools["load_html_from_url"](url, returnurl=True)

    tables = page.findAll('table')
    for table in tables:
        table.extract()

    if url.find('#') != -1:
        anchor = url.split('#')[1]
        page = str(page.find(id=anchor).findNext('p'))
    else:
        page = page.findAll('p')

        if str(page[0])[0:9] == '<p><span ' or self.tools['remove_html_tags'](str(page[0])).strip() == '':
            page = str(page[1].extract())
        else:
            page = str(page[0].extract())

    title = self.tools['remove_html_tags'](page)
    title = re.sub(r'\[.*?\]', '', title)
    title = title.replace("\n", " ")

    title = title[0:510]
    if title.rfind(".") != -1:
        title = title[0:title.rfind(".") + 1]

    return title, url


def get_wiki_file_description(self, url):
    page = self.tools["load_html_from_url"](url)

    try:
        desc = page.findAll("div", attrs={"class": "description en"})[0].getText(separator=" ")
    except:
        try:
            desc = page.find("th", attrs={"id": "fileinfotpl_desc"})
            desc = desc.findNextSibling("td").find("p").getText(separator=" ")
        except:
            try:
                desc = page.find("th", attrs={"id": "fileinfotpl_desc"})
                desc = desc.findNextSibling("td").find("div").getText(separator=" ")
            except:
                try:
                    desc = page.find("div", attrs={"id": "shared-image-desc"}).next.getText(separator=" ")
                except:
                    self.logger.debug("Couldn't find description for file %s" % url)
                    return

    desc = desc.replace("English:", "")
    desc = desc[0:510]
    if desc.rfind(".") != -1:
        desc = desc[0:desc.rfind(".") + 1]

    return desc.strip()

