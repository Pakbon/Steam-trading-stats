import re
import requests
import json
import csv
import datetime

import functions

def main():
    counter, boosters = countbpacks()
    #writecsv(counter, boosters)
    unpackbpacks()
    sql(counter, boosters)

def countbpacks():
    #scrape inventory
    steam = functions.load_id()
    url = 'https://steamcommunity.com/inventory/{}/753/6?count=10'.format(steam["steam64"])
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
    return counter, boosters

def unpackbpacks():
    'unpacks boosterpacks via ASF'
    steam = functions.load_id()
    url = '{}unpack%20{}'.format(steam["asfcommand"], steam["bot"])
    resp = requests.post(url, data='')
    resp = resp.json()
    if resp['Success']:
        return 0
    else:
        return 1

def writecsv(counter, boosters):
    with open('log/boosterpack.csv', 'a', newline='') as log:
        writer = csv.writer(log)
        writer.writerow([functions.Yday, counter, boosters])

def sql(counter, boosters):
    columns, values = '', ''
    columns += 'date, boosterpack_count'
    values += "\'{}\', \'{}\'".format(functions.Yday, counter)
    start = 0
    for name in boosters:
        columns += ',boosterpack_name{}'.format(str(start))
        values += ", \'{}\'".format(name[:-13])
        start += 1
    functions.write_sql('boosterpacks', columns, values)

if __name__ == '__main__':
    main()