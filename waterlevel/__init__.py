# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from urllib.request import urlopen
import ssl
from dateutil.parser import parse
import json
import unidecode

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


def clean_params(param):
    replace_list = ['.', "\'", " ?"]
    for r in replace_list:
        param = param.replace(r, '')

    return param


def decode_params(params):
    return clean_params(params['queryResult']['parameters']['river']), clean_params(params['queryResult']['parameters']['station'])


def get_station_id(river, station):
    rivers_file = open('./rivers.json')
    rivers = json.load(rivers_file)
    rivers_file.close()

    if river is None or river == '':
        for r in rivers:
            for s in rivers[r]:
                if unidecode.unidecode(s['station'].upper()) == unidecode.unidecode(station.upper()) or \
                  (s['detail'] is not None and unidecode.unidecode(s['detail'].upper()) == unidecode.unidecode(station.upper())):
                    return s['id']

    for r in rivers:
        if unidecode.unidecode(r.upper()) == unidecode.unidecode(river.upper()):
            print(r)
            for s in rivers[r]:
                if unidecode.unidecode(s['station'].upper()) == unidecode.unidecode(station.upper()) or \
                  (s['detail'] is not None and unidecode.unidecode(s['detail'].upper()) == unidecode.unidecode(station.upper())):
                    return s['id']

    return None


def get_fulfillment_text(data):
    river, station = decode_params(data)
    print(data)
    print(river)
    print(station)
    #if station is None or station == '' or river is None or river == '':
    #    return ''

    station_id = get_station_id(river, station)
    print(station_id)

    if station_id is None:
        return {'fulfillmentText': "Je n'ai pas trouvé cette station dans ma mémoire." }

    url = "https://www.vigicrues.gouv.fr/services/observations.xml/?CdStationHydro=" + station_id
    context = ssl._create_unverified_context()
    content = urlopen(url, context=context)
    soup = BeautifulSoup(content.read(), "xml")

    niveaux = list(soup.Donnees.Series.Serie.ObssHydro)
    last_niveau = None

    for n in niveaux:
        level = n.ResObsHydro.get_text()
        date = n.DtObsHydro.get_text()
        last_niveau = {'level': int(level), 'date': parse(date)}

    return { 'fulfillmentText': "Il y a " + str(last_niveau['level'] / 1000.).replace('.', ',') + " mètres à la station " + station }


@app.route('/water_level', methods=['POST'])
def get_water_level():
    data = json.loads(request.data.decode('utf-8'))

    return jsonify(get_fulfillment_text(data))


if __name__ == '__main__':
    app.run()
