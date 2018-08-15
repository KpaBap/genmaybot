import re, json, urllib.request
from urllib.parse import urlparse

class BeerCals:
    avg_fg = 1.012
    avg_beer_size_oz = 12
    avg_beer_size_ml = 330
    
    def __init__(self, abv, oz=None, ml=None):
        self.abv = abv
        self.oz = oz
        self.ml = ml

    def solve(self):
        if self.abv and self.oz:
            return self.abv_oz_nofg_to_cals(self.abv, self.oz)
        elif self.abv and self.ml:
            return self.abv_ml_nofg_to_cals(self.abv, self.ml)
        elif self.abv:
            return self.abv_oz_nofg_to_cals(self.abv, self.avg_beer_size_oz)
        else:
            return

    @staticmethod
    def oz_to_ml(oz):
        return float(oz) * 29.574

    @staticmethod
    def ml_to_oz(ml):
        return float(ml) / 29.574

    @staticmethod
    def plato_to_sg(plato): #Plato to specific gravity
        return plato / (258.6 - (( plato / 258.2) * 227.1)) + 1

    @staticmethod
    def sg_to_plato(sg):
        return -676.67+1286.4*sg-800.47*(sg**2)+190.74*(sg**3)

    @staticmethod
    def og_and_fg_to_abv(og,fg): #original gravity and final gravity to ABV
        og = float(og)
        fg = float(fg)
        return (1.05/0.70)*((og-fg)/fg)*100

    @staticmethod
    def og_and_abv_to_fg(og, abv): #convert from original gravity and ABV% to final gravity
        return og/((abv/150)+1)

    @staticmethod
    def abv_and_fg_to_sg(abv, fg):
        return (1+(abv/150))*fg

    @staticmethod
    def abv_and_ml_to_cals(abv, ml): #calorie count based on alcohol content only
        return float(ml)*(float(abv)/100)*7


    def fg_and_ml_to_cals(self, fg, ml): #calorie count based on residual sugars
        return float(ml)*(self.sg_to_plato(fg)/100)*3


    def og_abv_ml_to_cals(self, og, abv, ml):
        return int(round(self.abv_and_ml_to_cals(abv, ml) + (self.fg_and_ml_to_cals(self.og_and_abv_to_fg(og, abv), ml)),0))

    def og_abv_oz_to_cals(self, og, abv, oz):
        return self.og_abv_ml_to_cals(og, abv, self.oz_to_ml(oz))

    def abv_ml_nofg_to_cals(self, abv, ml): #Broad estimate based on just ABV and a typical FG of 1.012
        fg = self.avg_fg
        return int(round(self.abv_and_ml_to_cals(abv, ml) + self.fg_and_ml_to_cals(fg, ml),0))

    def abv_oz_nofg_to_cals(self, abv, oz): #Broad estimate again
        fg = self.avg_fg
        return int(round(self.abv_and_ml_to_cals(abv,  self.oz_to_ml(oz)) + self.fg_and_ml_to_cals(fg, self.oz_to_ml(oz)),0))

    @staticmethod
    def tokenize (calc_string):
        return re.split('\s', calc_string)




def advocate_beer(self, e):
    query = e.input
    #get the name, rating and style of a beer from beeradvocate.com
    url = self.tools['google_url']("site:beeradvocate.com " + query, "/beer/profile/[0-9]*?/[0-9]+")
    try:
        beerpage = self.tools["load_html_from_url"](url)
    except:
        self.logger.exception("Function advocate_beer Exception:")
        return

    beertitle = beerpage.head.title.string
    beertitle = beertitle[0:beertitle.find("|") - 1]

    grade = beerpage.find("span", {"class": "BAscore_big"}).string
    grade_wording = beerpage.find("a", href="/community/threads/beeradvocate-ratings-explained.184726/").b.string
    num_reviews = beerpage.find("span", {"class": "ba-ratings"}).string + " Ratings"
    style = beerpage.find("a", href=re.compile("/beer/style/[0-9]+/")).b.string
    abv = beerpage.find("a", href=re.compile("/beer/style/[0-9]+/")).next_sibling.replace("|", "").strip()
    cals = BeerCals(abv[:-1]).solve()
    
    if cals:
        cals = "Est. calories (12oz): %s" % cals


    e.output = "Beer: %s - Grade: %s [%s, %s] Style: %s ABV: %s %s [ %s ]" % (beertitle, 
                                                                           grade,
                                                                           grade_wording,
                                                                           num_reviews,
                                                                           style,
                                                                           abv, cals,
                                                                           self.tools['shorten_url'](url))
    return e
advocate_beer.command = "!ba"
advocate_beer.helptext = """\
Usage: !ba <beer name>
Example: !ba pliny the elder
Finds a given beer on beeradvocate.com and returns user ratings and beer info"""

def request_json(url):
    #if not request_json.token: #if we haven't found a valid client token, fall back to the public one
        #equest_json.token = self.botconfig["APIkeys"]["stravaToken"]


    response = urllib.request.urlopen(url)
    response = json.loads(response.read().decode('utf-8'))
    return response



def linear_dist(score, scaled_max, scaled_min, raw_max, raw_min):
    return scaled_max + ((scaled_min-scaled_max)/(raw_min-raw_max))*(score - raw_max)

def untappd_beer_search(self, e):
    clientid = self.botconfig["APIkeys"]["untappd_clientid"]
    clientsecret = self.botconfig["APIkeys"]["untappd_clientsecret"]

    auth = urllib.parse.urlencode({'client_id': clientid, 'client_secret': clientsecret})
    
    
    top_rating = 4.7
    lowest_rating = 1.1
    desired_top = 5
    desired_lowest = 1.5
    
    beername = e.input

    query = urllib.parse.urlencode({"q":beername})
    url = "https://api.untappd.com/v4/search/beer"

    url = "%s?%s&%s" % (url, query, auth)
    response = request_json(url)
    beerid = response['response']['beers']['items'][0]['beer']['bid']
    
    
    url = "https://api.untappd.com/v4/beer/info/%s?%s" % (beerid, auth)

    response = request_json(url)['response']['beer']

    beer_name = response['beer_name']
    beer_abv = response['beer_abv']
    beer_ibu = response['beer_ibu']
    beer_style = response['beer_style']
    
    beer_url = "https://untappd.com/b/%s/%s" % (response['beer_slug'], beerid)
    
    rating =  int(round(linear_dist(float(response['rating_score']), desired_top, desired_lowest, top_rating, lowest_rating)/desired_top*100, 0))
    rating_count = response['rating_count']

    if rating >=95:
        rating_word = "world-class"
    elif rating >= 90 and rating <= 94:
        rating_word = "outstanding"
    elif rating >=85 and rating <= 89:
        rating_word = "very good"
    elif rating >=80 and rating <= 84:
        rating_word = "good"
    elif rating >=70 and rating <=79:
        rating_word = "okay"
    elif rating >=60 and rating <=69:
        rating_word = "poor"
    elif rating < 60:
        rating_word = "awful"

    cals = BeerCals(beer_abv).solve()

    if cals:
        cals = "Est. calories (12oz): %s" % cals

    beerline = "Beer: %s - Grade: %s [%s, %s ratings] Style: %s ABV: %s%% %s [ %s ]" % (beer_name, 
                                                                           rating,
                                                                           rating_word,
                                                                           rating_count,
                                                                           beer_style,
                                                                           beer_abv, cals,
                                                                           self.tools['shorten_url'](beer_url))
     

    e.output = beerline
    return e



untappd_beer_search.command = "!beer"
untappd_beer_search.helptext = """\
Usage: !beer <beer name>
Example: !beer pliny the elder
Finds a given beer on Untappd and returns user ratings and beer info"""
