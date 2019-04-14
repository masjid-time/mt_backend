import os
import requests
from flask import jsonify
from flask_restful import Resource, abort
from webargs import fields
from webargs.flaskparser import use_args, parser

from mtapp import api
from mtapp.data import mosque_detail
from mtapp.util import item_mapper


class Mosques(Resource):

    location_args = {'lat': fields.Str(), 'lng': fields.Str()}

    @use_args(location_args)
    def get(self, args):
        try:
            lat, lng = args['lat'], args['lng']
        except KeyError:
            abort(404, errors='Latitude and longitude are not available')
        else:
            payload = {
                'key': os.environ['MAPS_KEY'],
                'location': f'{lat},{lng}',
                'rankby': 'distance',
                'type': 'mosque',
                'keyword': 'masjid'
            }
            resp = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=payload)
            results = resp.json()['results']
            mosque_list = [item_mapper(result, lat, lng) for result in results]
            return jsonify(mosque_list)


class MosqueDetail(Resource):
    def get(self, mosque_id):
        resp = {'found': False}
        for mosque in mosque_detail:
            if mosque['id'] == mosque_id:
                resp['found'] = True
                resp.update(mosque)
                break
        return jsonify(resp)


api.add_resource(Mosques, '/api/v1/mosques')
api.add_resource(MosqueDetail, '/api/v1/mosquedetail/<mosque_id>')


@parser.error_handler
def handle_request_parsing_error(err):
    abort(404, errors=err.messages)
