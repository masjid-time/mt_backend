from flask import jsonify
from flask_restful import Resource

from mtapp import api
from mtapp.data import mosque_list, mosque_detail


class Mosques(Resource):
    def get(self):
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
api.add_resource(MosqueDetail, '/api/v1/mosquedetail/<int:mosque_id>')
