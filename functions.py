"""functions used in other modules
"""

import requests
import json
import re
import datetime
import csv
from steam import webauth
from time import sleep
import _mysql

day = datetime.datetime.now()
day = day.replace(hour=0,minute=1,second=0,microsecond=0) - datetime.timedelta(1) #tracking YESTERDAY's haul
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
          ' AppleWebKit/537.36 (KHTML, like Gecko)'
          ' Chrome/68.0.3440.84 Safari/537.36'}

def login():
    'logs into steam, returns requests session with chrome headers and relevant cookies'

    steam = load_id()
    user = webauth.WebAuth(steam['username'], steam['password'])
    twofaurl = '{}2fa%20{}'.format(steam['asfcommand'], steam['bot'])
    twofa = requests.post(twofaurl,data='')
    twofa = twofa.json()['Result'][-5:]
    sleep(2) #since it can take a while for asf to respond
    steamsession = user.login(twofactor_code=twofa)
    steamsession.headers.update(header)
    return steamsession

def load_id():
    'returns dict of steam.json'
    with open('steam.json') as steam:
        read = json.loads(steam.read())
        return read

def post_comment(action, othername, steamid, steamsession, custcomment=''):
    'thank you for {action}, {othername}. steamid is steam64 of target profile. if custcomment, then other variables can be empty strings'
    sleep(5) # sleep for 5 seconds to avoid comment spam
    if custcomment:
        comment = custcomment
    else:
        comment = 'Thank you for {}, {}! :steamhappy:'.format(action, othername)
    commenturl = 'https://steamcommunity.com/comment/Profile/post/{}/-1/'.format(steamid)
    postdata = {'comment' : comment, 'count' : 6, 'sessionid' : steamsession.cookies.get('sessionid', domain='steamcommunity.com')}
    steamsession.post(commenturl, data=postdata)

def write_sql(table, column, value):
    'writes data in mysql. Takes 3 variables. table, column(s) and values. More than one column and value is possible'
    steam = load_id()
    db = _mysql.connect(steam['mysqlhost'], steam['mysqluser'], steam['mysqlpassword'], steam['mysqldatabase'])
    db.query('insert into {} ({}) values ({})'.format(table, column, value))