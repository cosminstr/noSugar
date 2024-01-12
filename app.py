from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime
from flask import redirect, url_for
import pandas as pd
import private

app = Flask(__name__)

secret_key = private.secret_key
connection_str = private.connection_string

app.secret_key = secret_key
app.config['MONGO_URI'] = connection_str

try:
    mongo = PyMongo(app)
    print("conectat cu DB!")
except Exception as e:
    print("eroare la conectarea cu DB: {e}")

from routes.home_route import *
from routes.user_routes import *

if __name__ == "__main__" : 
    app.run(debug = True)

