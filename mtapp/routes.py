import os
from datetime import datetime

import requests
from flask import jsonify
from flask_restful import Resource, abort
from webargs import fields
from webargs.flaskparser import use_args, parser

from mtapp import api, db
from mtapp.models import Timings
from mtapp.util import item_mapper, day_difference


class Mosques(Resource):
    location_args = {'lat': fields.Str(missing=''), 'lng': fields.Str(missing=''), 'place': fields.Str(missing='')}

    @use_args(location_args)
    def get(self, args):
        if args['lat'] and args['lng']:
            lat, lng = args['lat'], args['lng']
        elif args['place']:
            payload = {
                'key': os.environ['MAPS_KEY'],
                'input': args['place'],
                'inputtype': 'textquery',
                'fields': 'name,geometry,formatted_address'
            }
            resp = requests.get('https://maps.googleapis.com/maps/api/place/findplacefromtext/json', params=payload)
            result = resp.json()['candidates'][0]
            lat, lng = result['geometry']['location']['lat'], result['geometry']['location']['lng']
        else:
            abort(400, errors='Latitude, longitude or Place is not available')

        payload = {
            'key': os.environ['MAPS_KEY'],
            'location': f'{lat},{lng}',
            'rankby': 'distance',
            'type': 'mosque',
            'keyword': 'masjid'
        }
        resp = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=payload)
        results = resp.json()['results']
        mosque_list = {'results': [item_mapper(result, lat, lng) for result in results]}
        return jsonify(mosque_list)


class MosqueDetail(Resource):
    mosque_args = {'id': fields.Str(),
                   'place_id': fields.Str(),
                   'distance': fields.Str(),
                   'fazr': fields.Str(missing=''),
                   'zohr': fields.Str(missing=''),
                   'asr': fields.Str(missing=''),
                   'maghrib': fields.Str(missing=''),
                   'isha': fields.Str(missing=''),
                   }

    @use_args(mosque_args)
    def get(self, args):
        try:
            id, place_id = args['id'], args['place_id']
        except KeyError:
            abort(400, errors='Missing required parameters')
        else:
            payload = {
                'key': os.environ['MAPS_KEY'],
                'place_id': place_id,
                'fields': 'name,formatted_address,geometry,plus_code,url'
            }
            resp = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=payload)
            result = resp.json()['result']
            mosque_detail = {'name': result['name'],
                             'address': result['formatted_address'],
                             'url': result['url'],
                             'plus_code': result['plus_code'],
                             'distance': args['distance']}

        time_details = Timings.query.get(id)
        if time_details is None:
            time = {'time': {}, 'last_updated': ''}
        else:
            time = {'time': {'FAZR': time_details.time_fazr.strftime('%H:%M'),
                             'ZOHR': time_details.time_zohr.strftime('%H:%M'),
                             'ASR': time_details.time_asr.strftime('%H:%M'),
                             'MAGHRIB': time_details.time_maghrib.strftime('%H:%M'),
                             'ISHA': time_details.time_isha.strftime('%H:%M')},
                    'last_updated': day_difference(time_details.last_updated)}
        mosque_detail.update(time)

        return jsonify(mosque_detail)

    @use_args(mosque_args)
    def post(self, args):
        try:
            id = args.pop('id')
        except KeyError:
            abort(400, errors='Missing required parameters')
        else:
            time_data = {k: datetime.strptime(v, '%H:%M') for k, v in args.items()}
            data_to_save = Timings(id=id, time_fazr=time_data['fazr'],
                                   time_zohr=time_data['zohr'],
                                   time_asr=time_data['asr'],
                                   time_maghrib=time_data['maghrib'],
                                   time_isha=time_data['isha'],
                                   last_updated=datetime.now())

        try:
            db.session.add(data_to_save)
            db.session.commit()
        except:
            abort(500, errors='Unable to save data')
        return jsonify({'message': 'Data saved successfully'})


api.add_resource(Mosques, '/api/v1/mosques')
api.add_resource(MosqueDetail, '/api/v1/mosquedetail')


@parser.error_handler
def handle_request_parsing_error(err):
    abort(400, errors=err.messages)
