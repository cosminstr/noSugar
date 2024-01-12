from flask import jsonify, request, render_template
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import redirect, url_for
from app import app
from app import mongo
from users_routes import not_found

# SIGNUP ROUTE
@app.route('/signup', methods=['GET', 'POST'])
def add_user():

    if request.method == 'POST':

        if request.content_type == 'application/json':
            _json = request.json
            _name = _json['name']
            _password = _json['password']
            _confirm_password = _json['confirm_password']
        else:
            _name = request.form['name']
            _password = request.form['password']
            _confirm_password = request.form['confirm_password']

        _hashedpassword = generate_password_hash(_password)

        data = {
            'name': _name, 
            'password': _hashedpassword
        }

        if _name and _password and _confirm_password:
            if _password != _confirm_password:
                return render_template('signup.html', error = 'Parolele nu coincid.', name = _name), 400

            if mongo.db.Users.find_one({'name': _name}):
                return render_template('signup.html', error = 'Numele de utilizator există deja', name = _name), 400

            id = mongo.db.Users.insert_one(data)

            resp = jsonify("User adaugat cu succes")
            resp.status_code = 200
            user_id = str(id)

            return redirect(url_for('verify_user'))
        else:
            return not_found()
    else : 
        return render_template('signup.html')


# LOGIN ROUTE
@app.route('/login', methods=['GET', 'POST'])

def verify_user():
    if request.method == 'POST':
        if request.content_type == 'application/json':
            _json = request.json
            _name = _json['name']
            _password = _json['password']
        else:
            _name = request.form['name']
            _password = request.form['password']

        existing_user = mongo.db.Users.find_one({'name': _name})

        if existing_user : 
            if _name and _password:
                is_password_correct = check_password_hash(existing_user['password'], _password)

                if is_password_correct:
                    user_id = str(existing_user['_id'])
                    print(f"Login successful for user with ID: {user_id}")

                    return redirect(url_for('formular_user', id = user_id))
                else:
                    return render_template('login.html', error='Username sau parola gresite')
        else : 
            return render_template('login.html', error = 'Username inexistent')
    else : 
        return render_template('login.html')
