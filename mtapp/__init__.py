import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
cors = CORS(app, origins=['http://localhost:3000/*', 'https://prayertiming.herokuapp.com/*', 'https://masjidtime.herokuapp.com/*', 'https://www.masjidtime.com/*'])
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from mtapp import routes
