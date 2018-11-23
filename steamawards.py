'''Script to automatically get steamawards badges on multiple accounts
'''

import requests
import json
import csv

from time import sleep
from random import choice

import functions


def main():
    with open('accounts.csv') as accountfile:
        reader = csv.reader(accountfile,)
        accounts = list(reader)
        for row in accounts:
            session = functions.login(row[0], row[1], row[2])
            tasks(session)
            sleep(15)


def tasks(session):
    nominatedid = (644930, 387290, 252950, 33820958,
                   368340, 553310, 34900, 440)
    awarddict = {
        'sessionid': session.cookies.get('sessionid', domain='store.steampowered.com'),
        'nominatedid': 0,
        'categoryid': 0,
        'source': 3
    }

    for n in range(8):
        awarddict['categoryid'] = n+1
        nominateurl = 'https://store.steampowered.com/steamawards/nominategame'
        awarddict['nominatedid'] = nominatedid[n]
        session.post(nominateurl, data=awarddict, headers=functions.header)
        sleep(5)

    reviewurl = 'https://store.steampowered.com/friends/recommendgame'
    reviewcomment = (
        'pretty gud gaphics',
        'some nice gameplay',
        'awesome environment',
        'I like the mechanics'
    )
    reviewdict = {
        'appid': 440,
        'steamworksappid': 440,
        'comment': choice(reviewcomment),
        'is_public': 'false',
        'language': 'english',
        'received_compensation': 0,
        'disable_comments': 1,
        'sessionid': session.cookies.get('sessionid', domain='store.steampowered.com')
    }
    session.post(reviewurl, data=reviewdict, headers=functions.header)
    pass


if __name__ == '__main__':
    main()
