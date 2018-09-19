import re
import requests
import json
import csv
import datetime

import functions

day = datetime.datetime.now()
day = day.replace(hour=0,minute=1,second=0,microsecond=0) - datetime.timedelta(1) #tracking YESTERDAY's haul

def main():
    counter, boosters = countbpacks()
    writecsv(counter, boosters)
    #unpackbpacks()

def countbpacks():
    #scrape inventory
    file = functions.load_id()
    url = 'https://steamcommunity.com/inventory/{}/753/6?count=10'.format(file["steam64"])
    inventory = requests.get(url)

    #count boosters
    regex = re.compile(r'.*Booster Pack')
    boosters = []
    counter = 0
    for packs in inventory.json()['descriptions']:
        found = regex.search(packs['name'])
        if found == None:
            break
        else:
            boosters += [found.group()]
            counter += 1
    if len(boosters) == 0:
        boosters = ''
    else:
        boosters = ', '.join(map(str, boosters))
    
    return counter, boosters

def unpackbpacks():
    'unpacks boosterpacks via ASF'
    file = functions.load_id()
    url = '{}unpack%20{}'.format(file["asfcommand"], file["bot"])
    resp = requests.post(url, data='')
    resp = resp.json()
    if resp['Success']:
        return 0
    else:
        return 1

def writecsv(counter, boosters):
    with open('log/boosterpack.csv', 'a', newline='') as log:
        writer = csv.writer(log)
        writer.writerow([day.strftime("%Y-%m-%d"), counter, boosters])

if __name__ == '__main__':
    main()