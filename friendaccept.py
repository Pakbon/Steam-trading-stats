import requests
from bs4 import BeautifulSoup as bs
import json
import re
import time
from steam import webauth

import functions

def main():
    'run program'
    sesh = functions.login()
    fl_pending = souping(sesh)
    action(fl_pending, sesh)

def souping(sesh):
    steam = functions.load_id()
    pending = sesh.get('https://steamcommunity.com/id/{}/friends/pending'.format(steam['vanityurl']), headers=functions.header)
    soup = bs(pending.text)
    fl_pending = soup.select('.invite_row')
    return fl_pending

def action(fl_pending, sesh):
    steam = functions.load_id()
    url = 'https://steamcommunity.com/id/{}/friends/action'.format(steam['vanityurl'])
    for profiles in fl_pending:
        attrs = profiles.attrs
        post = {
            'sessionid' : sesh.cookies['sessionid'],
            'steamid' : steam['steam64'],
            'ajax' : '1',
            'action' : 'accept',
            'steamids[]' : attrs['data-steamid']
        }
        sesh.post(url, data=post, headers=functions.header)


main()
