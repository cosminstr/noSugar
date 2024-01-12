from flask import redirect, url_for
from app import app

@app.route('/')
def home():
    return redirect(url_for('add_user'))
