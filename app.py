from flask import Flask
from flask_pymongo import PyMongo
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
from routes.users_routes import *
from routes.register_routes import *

if __name__ == "__main__" : 
    app.run(debug = True)

