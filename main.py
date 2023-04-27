import werkzeug.exceptions
from flask import Flask, render_template, request, redirect, url_for, jsonify, json
from models import input_types, Form, db
from datetime import datetime
from config import settings


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{settings.database_username}:{settings.database_password}' \
                                        f'@{settings.database_hostname}:{settings.database_port}' \
                                        f'/{settings.database_name}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route('/', methods=['GET'])
def get_forms():
    forms = Form.query.all()
    return {"forms": forms}


@app.route('/create_form', methods=['GET', 'POST'])
def create_form():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        form_data = json.dumps(data.get('form_data'))

        # check if a form with similar name already exists.

        # existing_form = Form.query.filter_by(name=name).first()
        # if existing_form:
        #     return {"error": f"A form with the name: {name} already exists."}

        if not form_data:
            return {'error': 'Form Data field is required'}

        if not name:
            return {'error': 'Name field is required'}

        form = Form(name=name, form_data=form_data, created_at=datetime.utcnow())
        db.session.add(form)
        db.session.commit()

        return jsonify({'id': form.id, 'name': form.name, 'created_at': form.created_at, "form_data": form.form_data})

    return render_template('create_form.html', input_types=input_types)


@app.route('/edit_form/<int:form_id>', methods=['GET', 'PUT'])
def edit_form(form_id):
    form = Form.query.get(form_id)
    if form is None:
        return {'error': 'Form not found'}
    if request.method == 'PUT':
        data = request.get_json()
        name = data.get('name')

        # check if a form with similar name already exists.

        # existing_form = Form.query.filter_by(name=name).first()
        # if form.name != name:
        #     if name == existing_form.name:
        #         return {"error": f"A form with the name: {name} already exists."}

        form_data = json.dumps(data.get('form_data'))
        if name is not None:
            form.name = name
        form.form_data = form_data
        db.session.commit()
        return jsonify({'id': form.id, 'name': form.name, 'created_at': form.created_at, "form_data": form_data})
    return render_template('edit_form.html', form=form, input_types=input_types)


@app.route('/delete_form/<int:form_id>', methods=['POST'])
def delete_form(form_id):
    form = Form.query.get(form_id)
    if form is None:
        return {'error': 'Form not found'}
    db.session.delete(form)
    db.session.commit()
    return {"Message": "Form deleted"}


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
