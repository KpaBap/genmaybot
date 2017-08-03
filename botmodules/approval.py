import requests
import csv

def get_presidential_approval(self, event):
    """
    Gets presidential approval ratings from fivethirtyeight
    
    :param event: IRC event
    :return: IRC event with output set
    """
    data_url = "https://projects.fivethirtyeight.com/trump-approval-data/approval_topline.csv"
    human_link = self.tools['shorten_url']("https://projects.fivethirtyeight.com/trump-approval-ratings/")

    data = requests.get(data_url)

    data = data.content.decode('utf-8')
    data = data.splitlines()[0:4] # Only grab the top 3 lines from the CSV including the header

    reader = csv.DictReader(data)

    for row in reader:
        if row['subgroup'] == "All polls":
            break

    event.output = f"President: {row['president']} Approval: {round(float(row['approve_estimate']), 1)}% Disapproval: {round(float(row['disapprove_estimate']), 1)}% Date: {row['modeldate']} [ {human_link} ]"
    return event

get_presidential_approval.command = "!approval"
get_presidential_approval.helptext = get_presidential_approval.__doc__.splitlines()[0]

