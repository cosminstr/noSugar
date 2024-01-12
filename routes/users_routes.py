from flask import jsonify, request, render_template
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
import pandas as pd
from app import app
from app import mongo

# route used in the beginning while debugging in POSTMAN
@app.route('/users/<id>', methods = ['GET'])
def user(id) : 
    user = mongo.db.Users.find_one({'_id' : ObjectId(id)})
    resp  = dumps(user)
    return resp


# form route
@app.route('/users/<id>/formular', methods=['GET', 'POST'])

def formular_user(id):
    user = mongo.db.Users.find_one({'_id': ObjectId(id)})
    user_name = user.get('name', '')

    if request.method == 'POST':
        if request.content_type == 'application/json':
            _json = request.json
            _bloodsugar = _json['bloodsugar']
            _insulindose = _json['insulindose']
            _nrmese = _json['nr_mese']
            _activitate = _json['activitate']
        else:
            _bloodsugar = int(request.form['bloodsugar'])
            _insulindose = int(request.form['insulindose'])
            _nrmese = int(request.form['nr_mese'])
            _activitate = int(request.form['activitate'])

        data_form = {
            'user_id': id, 
            'bloodsugar': _bloodsugar, 
            'insulindose': _insulindose, 
            'nr_mese': _nrmese, 
            'activitate' : _activitate, 
            'timestamp': datetime.utcnow()
        }

        if data_form:
            id2 = mongo.db.Forms.insert_one(data_form)
            resp = jsonify("Formular completat")
            resp.status_code = 200
            return render_template('formular_complet.html', id = str(id), message = 'Formular completat cu succes',name=user_name)
        else:
            return not_found()
        
    else :     
        return render_template('formular.html', id=str(id), name = user_name)


# dashboard route
@app.route('/users/<id>/dashboard', methods=['GET'])

def dashboard(id):
    user = mongo.db.Users.find_one({'_id': ObjectId(id)})

    if user:
        user_name = user.get('name', '')

        forms_data = list(mongo.db.Forms.find({'user_id': id}, {'_id': 0, 'timestamp': 0, 'user_id': 0}))

        if forms_data:
            chart_data = {
                'labels': [form.get('timestamp', '') for form in forms_data],
                'bloodsugar': [form.get('bloodsugar', 0) for form in forms_data],
                'insulindose': [form.get('insulindose', 0) for form in forms_data],
                'nr_mese': [form.get('nr_mese', 0) for form in forms_data],
                'activitate': [form.get('activitate', 0) for form in forms_data],
            }

            return render_template('dashboard.html', id=str(id), name=user_name, chart_data=chart_data)
    return render_template('formular_complet.html', id = str(id), message = 'Completeaza formularul pentru a putea vizualiza statistici',name=user_name)


# reminders route
@app.route('/users/<id>/remindere', methods = ['GET', 'POST'])

def user_form(id):

    user = mongo.db.Users.find_one({'_id': ObjectId(id)})
    user_name = user.get('name', '')

    return render_template('calendar.html', id = str(id), name=user_name)

# analysis route
@app.route('/users/<id>/analiza', methods = ['GET'])
def analiza(id):
    user = mongo.db.Users.find_one({'_id': ObjectId(id)})
    user_name = user.get('name', '')

    forms_data = list(mongo.db.Forms.find({'user_id': id}, {'_id': 0, 'timestamp': 0, 'user_id': 0}))

    if forms_data:
        df = pd.DataFrame(forms_data)
        
        # Realizează analize statistice cu Pandas aici
        blood_sugar_stats = df['bloodsugar'].describe().round(2)
        insulindose_stats = df['insulindose'].describe().round(2)
        nr_mese_stats = df['nr_mese'].describe().round(2)
        activitate_stats = df['activitate'].describe().round(2)

        return render_template('analiza.html', id=str(id), name=user_name,
                               blood_sugar_stats=blood_sugar_stats,
                               insulindose_stats=insulindose_stats,
                               nr_mese_stats=nr_mese_stats,
                               activitate_stats=activitate_stats)
    else:
        return render_template('formular_complet.html', id = str(id), message = 'Completeaza formularul pentru a putea vizualiza statistici',name=user_name)

# function to remove all 'char' datatypes from a file
def string_to_array(input_string):
    try:
        result_array = [int(num) for num in input_string.split(',')]
        return result_array
    except ValueError:
        print("Invalid input format. Please provide a string of comma-separated integers.")
        return None
from flask import Response

# export route
@app.route('/users/<id>/export', methods=['GET'])
def export_user_data(id):
    forms_data = list(mongo.db.Forms.find({'user_id': id}, {'_id': 0, 'timestamp': 0, 'user_id': 0}))
    zi = 1

    if forms_data:
        csv_data = ""
                                                                                                                                                                                        
        for form in forms_data:
            # csv_data += f"ziua {zi} : {form['bloodsugar']} mg/dL, {form['insulindose']} doze, {form['nr_mese']} mese, {form['activitate']} minute de activitate\n"
            csv_data += f"{form['bloodsugar']}, {form['insulindose']}, {form['nr_mese']}, {form['activitate']}\n"
            zi = zi + 1
        return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=date_user.csv'})

    return not_found()

# import route
@app.route('/users/<id>/import', methods=['POST'])
def import_data(id):
    try:
        import_file = request.files['import_file']

        if import_file:
            content = import_file.read().decode('utf-8')
            lines = content.split('\n')[2:]

            json_data = []

            for line in lines:
                cleaned_line = ''.join(char for char in line if char.isnumeric() or char in [',', ':'])

                if ':' in cleaned_line:
                    cleaned_line = cleaned_line.split(':', 1)[1].strip()
                    data_array = string_to_array(cleaned_line)
                    data_form = {
                        'user_id': id,
                        'bloodsugar': data_array[0],
                        'insulindose': data_array[1],
                        'nr_mese': data_array[2],
                        'activitate': data_array[3],
                        'timestamp': datetime.utcnow()
                    }
                    id2 = mongo.db.Forms.insert_one(data_form)
                    json_data.append(data_form)

            response_data = {'data': json_data, 'refresh_page': True}
            return jsonify(response_data), 200
        
        else:
            return jsonify({'error': 'fisier invalid'}), 400
    except Exception as e:

        return jsonify({'error': f'Error importing data. Please check your file. {str(e)}'}), 500


# route used in the beginning while debugging in POSTMAN
@app.route('/users', methods = ['GET'])
def users() : 
    users = mongo.db.Users.find()
    resp = dumps(users)
    return resp


# error handling  
@app.errorhandler(404)
def not_found(error = None) : 

    message = { 
        'status' : 404,
        'message' : "user negasit " + request.url
    }

    resp = jsonify(message)
    resp.status_code = 404

    return resp