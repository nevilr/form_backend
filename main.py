from flask import Flask, render_template, request, redirect, url_for, jsonify
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
        name = request.form['name']
        form = Form(name=name, created_at=datetime.utcnow())
        db.session.add(form)
        db.session.commit()
        return redirect(url_for('get_forms'))
    return render_template('create_form.html', input_types=input_types)


@app.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
def edit_form(form_id):
    form = Form.query.get(form_id)
    if form is None:
        return {'error': 'Form not found'}
    if request.method == 'POST':
        name = request.form['name']
        form.name = name
        db.session.commit()
        return redirect(url_for('get_forms'))
    return render_template('edit_form.html', form=form, input_types=input_types)


@app.route('/delete_form/<int:form_id>', methods=['POST'])
def delete_form(form_id):
    form = Form.query.get(form_id)
    if form is None:
        return {'error': 'Form not found'}
    db.session.delete(form)
    db.session.commit()
    return redirect(url_for('get_forms'))


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
