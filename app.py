from flask import Flask
from flask_pymongo import PyMongo
import private2

app = Flask(__name__)

secret_key = private2.secret_key
connection_str = private2.connection_string

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

