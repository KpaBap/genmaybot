import re

def get_chainlove(self, e):
    page = self.tools["load_html_from_url"]("http://chainlove.com/")
    title = str(page.head.title.text).replace("Chainlove.com:" , "http://chainlove.com -")
    page = page.text
    timeleft = int(re.search("(BCNTRY.setupTimerBar\()(\d+)(,\d+\))", page).group(2))
    qtyleft = re.search("(BCNTRY.total_qty_bar.set_data\()(\d+)(,\d+\))", page).group(2)
    
    e.output = "{} - {}:{:02} Left - {} Remaining".format(title, timeleft//60, timeleft%60,  qtyleft)
    
    return e
get_chainlove.command = "!chainlove"
get_chainlove.helptext = """\
Usage: !chainlove
Shows the current deal on Chainlove.com and the time and quantity remaining"""
