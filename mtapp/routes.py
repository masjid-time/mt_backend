from flask import jsonify
from flask_restful import Resource

from mtapp import api
from mtapp.data import mosque_list


class Mosques(Resource):
    def get(self):
        return jsonify(mosque_list)


api.add_resource(Mosques, '/api/v1/mosques')
