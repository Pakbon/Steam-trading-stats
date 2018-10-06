import requests
from bs4 import BeautifulSoup as bs
import json
import re
import time

import functions

steam = functions.load_id()

def main():
    'run program'
    sesh = functions.login(steam['bot'], steam['username'], steam['password'])
    fl_pending = souping(sesh)
    action(fl_pending, sesh)

def souping(sesh):
    pending = sesh.get('https://steamcommunity.com/id/{}/friends/pending'.format(steam['vanityurl']), headers=functions.header)
    soup = bs(pending.text, features='html.parser')
    fl_pending = soup.select('.invite_row')
    return fl_pending

def action(fl_pending, sesh):
    url = 'https://steamcommunity.com/id/{}/friends/action'.format(steam['vanityurl'])
    for profiles in fl_pending:
        attrs = profiles.attrs
        post = {
            'sessionid' : sesh.cookies.get('sessionid', domain='steamcommunity.com'),
            'steamid' : steam['steam64'],
            'ajax' : '1',
            'action' : 'accept',
            'steamids[]' : attrs['data-steamid']
        }
        sesh.post(url, data=post, headers=functions.header)

if __name__ == '__main__':
    main()
