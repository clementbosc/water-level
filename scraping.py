from urllib.request import urlopen
import ssl
import re
from bs4 import BeautifulSoup
import json
import unidecode



def get_bassins():
    context = ssl._create_unverified_context()
    webpage = urlopen("https://www.vigicrues.gouv.fr/", context=context).read()
    soup = BeautifulSoup(webpage, "lxml")
    map_areas = soup.find_all("area")
    bassins = []

    for area in map_areas:
        bassins.append(area.get('href')[1:])

    return bassins


def split_title(title):
    groups = re.match(r'^(.[^\[\]\(\)]+)\s(?:\[(.+)\]\s)?\((.+)\)$', title)
    return groups.groups()


def get_stations(bassin_url):
    context = ssl._create_unverified_context()
    webpage = urlopen("https://www.vigicrues.gouv.fr"+bassin_url, context=context).read()
    soup = BeautifulSoup(webpage, "lxml")
    map = soup.find(id="MAP1")
    map_areas = map.find_all("area", {"shape": 'circle'})
    stations = []

    for area in map_areas:
        label, details, river = split_title(area.get('title'))
        s = { 'station_id': area.get('href')[-10:], 'label': label, 'details': details, 'river': river }
        stations.append(s)

    return stations


def get_synonyms(word):
    word = word.replace('(', '')
    word = word.replace(')', '')
    word = word.replace('[', '')
    word = word.replace(']', '')

    synonyms = [word]

    if word.replace('-', ' ') not in synonyms:
        synonyms.append(word.replace('-', ' '))
    if word.lower().replace('-', ' ') not in synonyms:
        synonyms.append(word.lower().replace('-', ' '))
    if word.lower() not in synonyms:
        synonyms.append(word.lower())
    if word.lower().replace('st-', 'saint ') not in synonyms:
        synonyms.append(word.lower().replace('st-', 'saint '))
    if word.lower().replace('st-', 'saint-') not in synonyms:
        synonyms.append(word.lower().replace('st-', 'saint-'))
    if word.replace('St-', 'Saint ') not in synonyms:
        synonyms.append(word.replace('St-', 'Saint '))
    if word.replace('St-', 'Saint-') not in synonyms:
        synonyms.append(word.replace('St-', 'Saint-'))
    if word.lower().replace('ste-', 'saint ') not in synonyms:
        synonyms.append(word.lower().replace('ste-', 'saint '))
    if word.lower().replace('ste-', 'saint-') not in synonyms:
        synonyms.append(word.lower().replace('ste-', 'saint-'))
    if word.replace('Ste-', 'Saint ') not in synonyms:
        synonyms.append(word.replace('Ste-', 'Saint '))
    if word.replace('Ste-', 'Saint-') not in synonyms:
        synonyms.append(word.replace('Ste-', 'Saint-'))

    if unidecode.unidecode(word.replace('-', ' ')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.replace('-', ' ')))
    if unidecode.unidecode(word.lower().replace('-', ' ')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.lower().replace('-', ' ')))
    if unidecode.unidecode(word.lower()) not in synonyms:
        synonyms.append(unidecode.unidecode(word.lower()))
    if unidecode.unidecode(word.lower().replace('st-', 'saint ')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.lower().replace('st-', 'saint ')))
    if unidecode.unidecode(word.lower().replace('st-', 'saint-')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.lower().replace('st-', 'saint-')))
    if unidecode.unidecode(word.replace('St-', 'Saint ')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.replace('St-', 'Saint ')))
    if unidecode.unidecode(word.replace('St-', 'Saint-')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.replace('St-', 'Saint-')))
    if unidecode.unidecode(word.lower().replace('ste-', 'saint ')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.lower().replace('ste-', 'saint ')))
    if unidecode.unidecode(word.lower().replace('ste-', 'saint-')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.lower().replace('ste-', 'saint-')))
    if unidecode.unidecode(word.replace('Ste-', 'Saint ')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.replace('Ste-', 'Saint ')))
    if unidecode.unidecode(word.replace('Ste-', 'Saint-')) not in synonyms:
        synonyms.append(unidecode.unidecode(word.replace('Ste-', 'Saint-')))

    return synonyms



def create_json_river_file():
    bassins = get_bassins()

    rivers = {}
    outpath = 'rivers.json'

    for bassin_url in bassins:
        stas = get_stations(bassin_url)
        for s in stas:
            line = {'station': s['label'], 'detail': s['details'], 'id': s['station_id']}
            if s['river'] in rivers:
                rivers[s['river']].append(line)
            else:
                rivers[s['river']] = [line]

    with open(outpath, 'w') as fp:
        json.dump(rivers, fp)


def create_entities_rivers_csv():
    bassins = get_bassins()

    rivers = []
    outpath = 'rivers.csv'
    outfile = open(outpath, 'w')

    for bassin_url in bassins:
        stas = get_stations(bassin_url)
        for s in stas:
            if s['river'] not in rivers:
                rivers.append(s['river'])

    for r in rivers:
        outfile.write("\""+r+"\",\""+r+"\"\n")

    outfile.close()


def create_entities_stations_csv():
    bassins = get_bassins()

    outpath = 'stations.csv'
    outfile = open(outpath, 'w')

    for bassin_url in bassins:
        stas = get_stations(bassin_url)
        for s in stas:
            outfile.write("\"" + s['label'] + "\",\"" + "\",\"".join(get_synonyms(s['label'])) + "\""+(",\""+"\",\"".join(get_synonyms(s['details']))+"\"" if s['details'] is not None else '')+"\n")

    outfile.close()


if __name__ == '__main__':
    #create_json_river_file()
    print('hello')
    #create_entities_rivers_csv()
    create_entities_stations_csv()