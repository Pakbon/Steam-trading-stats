"""Posts a Comment on the 'dead game comment' meme in Payday 2 news articles
"""
import requests
import re
import shelve
from bs4 import BeautifulSoup as bs
from random import choice
from time import sleep

import functions

steam = functions.load_id()

def main():
    counter = 0
    while True:
        announceurl, art = article()
        found, options = comments(art)
        if found:
            creds = functions.login(steam['bot'],steam['username'],steam['password'])
            commenter(creds, announceurl, found, options=options)
            savefile = shelve.open('paydaytwo.shv')                
            try:
                savefile[functions.Tday.date().strftime('%Y-%m-%d')] += 1                
            except:
                savefile[functions.Tday.date().strftime('%Y-%m-%d')] = 1
            break   
        else: #try a few more time before giving up, interval of 10 seconds
            counter += 1
            if counter == 12:
                break
            else:
                sleep(10)

def article():
    #find the latest article posted
    appid = 'appid=218620'
    count = 'count=1'
    maxlength = 'maxlength=1'
    url = 'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?{}&{}&{}'.format(appid, count, maxlength)
    newsreq = requests.get(url, headers=functions.header)
    newsreq = newsreq.json()

    announceurl = newsreq['appnews']['newsitems'][0]['url']
    announce = requests.get(announceurl, headers=functions.header)
    return announce.url, announce.text

def comments(art):
    #find the comment section in article
    #filter for comment
    #if found, return name of commenter
    soup = bs(art, features='html.parser')
    replies = soup.select('.commentthread_comment')
    
    regex = replies[0].find(string=re.compile(r'^[\s]*(((d[ea]{1,2}d)|([game]{3,4})).?){2}', re.IGNORECASE))
    if regex:
        name = replies[0].bdi.contents[0]
        return name, 0
    
    regex = replies[8].find(string=re.compile(r'^[\s]*F{1,}[\s]+'))
    if regex:
        name = replies[0].bdi.contents[0]
        return name, 1
    
    regex = replies[0].find(string=re.compile(r'^[\s](d[ea]{1,2}d bain)[\s]*', re.IGNORECASE))
    if regex:
        name = replies[0].bdi.contents[0]
        return name, 2
    
    regex = replies[0].find(string=re.compile(r'^[\s](a?li[vf]{1}e game|und[ea]{1,2}d [game]{3,4})[\s]*', re.IGNORECASE))
    if regex:
        name = replies[0].bdi.contents[0]
        return name, 3

    else:
        return 0, 0

def commenter(creds, announceurl, name, options=0):
    #post comment
    articleid = str(announceurl[-19:]) +'/'
    url = 'https://steamcommunity.com/comment/ClanAnnouncement/post/103582791433980119/' + articleid
    phrases = {
        0:['As it may be', 'Maybe it is', 'It conceivably is', 'Perhaps it is', 'It possibly is', 'Perchance it is', 'Perhaps it is', 'It might be', 'It could be', 'It can be', 'It feasibly is'],
        1:['Thank you for paying your respects', 'Respect has been paid', 'You have paid your respects'],
        2:['Perhaps he\'s wondering why someone would shoot a man, before throwing him out of a plane?','No one cared who I was until I put on the mask.','It would be extremely painful.','Crashing this plane... with no survivors!'],
        3:['As it may not be', 'Maybe it is\'nt','Maybe not', 'Perhaps it is not']
    }
    payload = {'comment' : '@' + name + '\n' + choice(phrases[options]), 'count' : 10, 'sessionid' : creds.cookies.get('sessionid', domain='steamcommunity.com'), 'extended_data': {'appid':218620}, 'feature2': -1}
    creds.post(url, headers=functions.header, data=payload)

main()
