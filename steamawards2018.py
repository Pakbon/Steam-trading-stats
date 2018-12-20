"""automatically vote in steam awards on multiple accounts
"""

import requests
import csv
from time import sleep

import functions

def main():
    with open('accounts.csv') as accountfile:
        reader = csv.reader(accountfile,)
        accounts = list(reader)
        for row in accounts:
            session = functions.login(row[0], row[1], row[2])
            vote(session)
            sleep(15)

def vote(session):
    url = 'https://store.steampowered.com/salevote'
    sessionid = session.cookies.get('sessionid', domain='store.steampowered.com')
    votedict = { 
        26 : 578080, 
        27 : 611670,
        28 : 271590,
        29 : 33075774,
        30 : 292030,
        31 : 218620,
        32 : 612880,
        33 : 252950 
        }
    for voteid, appid in votedict.items():
        data = {
            'sessionid' : sessionid,
            'voteid' : voteid,
            'appid' : appid,
            'developerid' : 0
        }
        if voteid == 29:
            data['appid'] = 0
            data['developerid'] = appid
        session.post(url, data, headers=functions.header)
        sleep(5)



if __name__ == '__main__':
    main()