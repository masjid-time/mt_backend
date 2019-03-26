from flask import Flask
from flask_cors import CORS
from flask_restful import Api

app = Flask(__name__)
cors = CORS(app, origins=['http://localhost:3000/*', 'https://prayertiming.herokuapp.com/*'])
api = Api(app)

from mtapp import routes
