import os
from datetime import datetime

import requests
from flask import jsonify, request
from flask_restful import Resource, abort
from webargs import fields
from webargs.flaskparser import use_args, parser

from mtapp import api, db
from mtapp.models import Timings
from mtapp.util import item_mapper, day_difference


class Mosques(Resource):
    location_args = {'lat': fields.Str(missing=''),
                     'lng': fields.Str(missing=''),
                     'place': fields.Str(missing=''),
                     'next_page_token': fields.Str(missing='')}

    @use_args(location_args)
    def get(self, args):
        if args['next_page_token']:
            pagetoken, pos = args['next_page_token'].split('@')
            lat, lng = pos.split(',')
            payload = {
                'key': os.environ['MAPS_KEY'],
                'pagetoken': pagetoken
            }
        elif args['lat'] and args['lng']:
            lat, lng = args['lat'], args['lng']
            payload = {
                'key': os.environ['MAPS_KEY'],
                'location': f'{lat},{lng}',
                'rankby': 'distance',
                'type': 'mosque',
                'keyword': 'masjid'
            }
        elif args['place']:
            findplace_payload = {
                'key': os.environ['MAPS_KEY'],
                'input': args['place'],
                'inputtype': 'textquery',
                'fields': 'name,geometry,formatted_address'
            }
            findplace_resp = requests.get('https://maps.googleapis.com/maps/api/place/findplacefromtext/json',
                                          params=findplace_payload)
            try:
                result = findplace_resp.json()['candidates'][0]
            except IndexError:
                return jsonify({'results': ''})
            else:
                lat, lng = result['geometry']['location']['lat'], result['geometry']['location']['lng']
                payload = {
                    'key': os.environ['MAPS_KEY'],
                    'location': f'{lat},{lng}',
                    'rankby': 'distance',
                    'type': 'mosque',
                    'keyword': 'masjid'
                }
        else:
            abort(400, errors='Bad request')

        resp = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=payload)
        if resp.json().get('next_page_token') is None:
            mosque_list = {'next_page_token': ''}
        else:
            mosque_list = {'next_page_token': f"{resp.json().get('next_page_token')}@{lat},{lng}"}
        results = resp.json()['results']
        mosque_list.update({'results': [item_mapper(result, lat, lng) for result in results]})

        return jsonify(mosque_list)


class MosqueDetail(Resource):
    mosque_args = {'id': fields.Str(),
                   'place_id': fields.Str(),
                   'distance': fields.Str()
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
            mosque_detail = {'id': id,
                             'name': result['name'],
                             'address': result['formatted_address'],
                             'url': result['url'],
                             'plus_code': result['plus_code'],
                             'distance': args['distance']}

        time_details = Timings.query.get(id)
        if time_details is None:
            time = {'time': {}, 'last_updated': ''}
        else:
            time = {'time': {'FAJR': time_details.fajr.strftime('%H:%M'),
                             'DHUHR': time_details.dhuhr.strftime('%H:%M'),
                             'ASR': time_details.asr.strftime('%H:%M'),
                             'MAGHRIB': time_details.maghrib.strftime('%H:%M'),
                             'ISHA': time_details.isha.strftime('%H:%M')},
                    'last_updated': day_difference(time_details.last_updated)}
        mosque_detail.update(time)

        return jsonify(mosque_detail)

    def post(self):
        args = request.get_json()
        try:
            id = args.pop('id')
        except KeyError:
            abort(400, errors='Missing required parameters')
        else:
            time_data = {k: datetime.strptime(v, '%H:%M') for k, v in args.items()}
            data_to_save = Timings(id=id, time_fazr=time_data['FAJR'],
                                   time_zohr=time_data['DHUHR'],
                                   time_asr=time_data['ASR'],
                                   time_maghrib=time_data['MAGHRIB'],
                                   time_isha=time_data['ISHA'],
                                   last_updated=datetime.now())

        try:
            db.session.add(data_to_save)
            db.session.commit()
        except Exception as e:
            abort(500, errors=f'Unable to save data due to error {e}')
        return jsonify({'message': 'Data saved successfully'})

    def put(self):
        args = request.get_json()
        try:
            id = args.pop('id')
        except KeyError:
            abort(400, errors='Missing required parameters')
        else:
            time_details = Timings.query.get(id)
            time_data = {k: datetime.strptime(v, '%H:%M') for k, v in args.items()}
            time_details.fajr = time_data['FAJR']
            time_details.dhuhr = time_data['DHUHR']
            time_details.asr = time_data['ASR']
            time_details.maghrib = time_data['MAGHRIB']
            time_details.isha = time_data['ISHA']
            time_details.last_updated = datetime.now()

        try:
            db.session.commit()
        except Exception as e:
            abort(500, errors=f'Unable to save data due to error {e}')

        return jsonify({'message': 'Data saved successfully'})


api.add_resource(Mosques, '/api/v1/mosques')
api.add_resource(MosqueDetail, '/api/v1/mosquedetail')


@parser.error_handler
def handle_request_parsing_error(err):
    abort(400, errors=err.messages)
