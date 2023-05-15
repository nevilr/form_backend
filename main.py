from models import input_types, Form, db, UserData
from flask import Flask, render_template, request, redirect, url_for, jsonify, json
from datetime import datetime
from config import settings
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}"
    f"/{settings.database_name}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


# form routes
@app.route("/", methods=["GET"])
def get_forms():
    forms = Form.query.all()
    forms_list = []

    for form in forms:
        form_dict = {
            "id": form.id,
            "name": form.name,
            "created_at": form.created_at,
            "data": json.loads(form.data),
            "slug": form.slug,
        }
        forms_list.append(form_dict)

    return jsonify({"forms": forms_list})


@app.route("/<string:slug>", methods=["GET"])
def get_form(slug):
    form = Form.query.filter_by(slug=slug).first()
    if not form:
        return jsonify({"error": "Form not found"}), 404

    form_dict = {
        "id": form.id,
        "name": form.name,
        "created_at": form.created_at,
        "data": json.loads(form.data),
        "slug": form.slug,
    }

    return jsonify(form_dict)


@app.route("/create_form", methods=["GET", "POST"])
def create_form():
    if request.method == "POST":
        form_data = request.get_json()
        name = form_data.get("name")
        slug = form_data.get("slug")
        data = json.dumps(form_data.get("data"))

        # check if a form with similar name already exists.

        # existing_form = Form.query.filter_by(name=name).first()
        # if existing_form:
        #     return {"error": f"A form with the name: {name} already exists."}
        existing_form = Form.query.filter_by(slug=slug).first()

        if existing_form:
            return {"error": f"A form with the slug: {slug} already exists."}

        if not data:
            return {"error": "Form Data field is required"}

        if not name:
            return {"error": "Name field is required"}

        form = Form(name=name, data=data, created_at=datetime.utcnow(), slug=slug)
        db.session.add(form)
        db.session.commit()

        return jsonify(
            {
                "id": form.id,
                "name": form.name,
                "created_at": form.created_at,
                "data": form.data,
                "slug": form.slug,
            }
        )

    return render_template("create_form.html", input_types=input_types)
    # return jsonify({"input_types": input_types})


@app.route("/edit_form/<int:id>", methods=["GET", "PUT"])
def edit_form(id):
    form = Form.query.filter_by(id=id).first()

    if form is None:
        return {"error": "Form not found"}
    if request.method == "PUT":
        data = request.get_json()
        name = data.get("name")
        slug = data.get("slug")

        # check if a form with similar name already exists.

        # existing_form = Form.query.filter_by(name=name).first()
        # if form.name != name:
        #     if name == existing_form.name:
        #         return {"error": f"A form with the name: {name} already exists."}

        data = json.dumps(data.get("data"))

        # check if a form with similar slug already exists.
        # existing_form = Form.query.filter_by(slug=slug).first()

        # if existing_form:
        #     return {"error": f"A form with the slug: {slug} already exists."}

        if name is not None:
            form.name = name

        if slug is not None:
            form.slug = slug

        form.data = data
        db.session.commit()

        return jsonify(
            {
                "id": form.id,
                "name": form.name,
                "created_at": form.created_at,
                "data": data,
                "slug": form.slug,
            }
        )
    return render_template("edit_form.html", form=form, input_types=input_types)


@app.route("/delete_form/<int:id>", methods=["DELETE"])
def delete_form(id):
    form = Form.query.filter_by(id=id).first()
    saved_forms = UserData.query.filter_by(form_id=id).all()

    if form is None:
        return {"error": "Form not found"}

    if saved_forms:
        for saved_form in saved_forms:
            db.session.delete(saved_form)
            db.session.commit()

    db.session.delete(form)
    db.session.commit()

    return {"Message": "Form deleted"}


# -------------------------------------------------------------user routes-------------------------------------------------------------
@app.route("/user_inputs", methods=["GET"])
def get_user_inputs():
    user_inputs = UserData.query.all()
    user_inputs_list = []

    for user_input in user_inputs:
        user_input_dict = {
            "id": user_input.id,
            "submitted_at": user_input.submitted_at,
            "input_data": json.loads(user_input.input_data),
            "form_id": user_input.form_id,
        }
        user_inputs_list.append(user_input_dict)

    return jsonify({"user_inputs": user_inputs_list})


@app.route("/<int:id>", methods=["GET"])
def get_user_input(id):
    user_input = UserData.query.filter_by(id=id).first()
    if not user_input:
        return jsonify({"error": "User Input not found"}), 404

    user_input_dict = {
        "id": user_input.id,
        "submitted_at": user_input.submitted_at,
        "input_data": json.loads(user_input.input_data),
        "form_id": user_input.form_id,
    }

    return jsonify(user_input_dict)


@app.route("/create_user_input", methods=["GET", "POST"])
def create_user_input():
    if request.method == "POST":
        user_input_data = request.get_json()
        input_data = json.dumps(user_input_data.get("input_data"))
        form_id = user_input_data.get("form_id")

        # check if a form with similar name already exists.

        # existing_form = Form.query.filter_by(name=name).first()
        # if existing_form:
        #     return {"error": f"A form with the name: {name} already exists."}
        # existing_form = Form.query.filter_by(slug=slug).first()

        # if existing_form:
        #     return {"error": f"A form with the slug: {slug} already exists."}

        if not input_data:
            return {"error": "User Input Data field is required"}

        if not form_id:
            return {"error": "Form Id is required"}

        user_input = UserData(
            input_data=input_data, submitted_at=datetime.utcnow(), form_id=form_id
        )
        db.session.add(user_input)
        db.session.commit()

        return jsonify(
            {
                "id": user_input.id,
                "submitted_at": user_input.submitted_at,
                "input_data": user_input.input_data,
                "form_id": user_input.form_id,
            }
        )

    return render_template("create__user_input.html", input_types=input_types)
    # return jsonify({"input_types": input_types})


@app.route("/edit_user_input/<int:id>", methods=["GET", "PUT"])
def edit_user_input(id):
    user_input = UserData.query.filter_by(id=id).first()

    if user_input is None:
        return {"error": "User Data not found"}
    if request.method == "PUT":
        input_data = request.get_json()

        # check if a form with similar name already exists.

        # existing_form = Form.query.filter_by(name=name).first()
        # if form.name != name:
        #     if name == existing_form.name:
        #         return {"error": f"A form with the name: {name} already exists."}

        input_data = json.dumps(input_data.get("input_data"))

        # check if a form with similar slug already exists.
        # existing_form = Form.query.filter_by(slug=slug).first()

        # if existing_form:
        #     return {"error": f"A form with the slug: {slug} already exists."}

        user_input.input_data = input_data
        db.session.commit()

        return jsonify(
            {
                "id": user_input.id,
                "submitted_at": user_input.submitted_at,
                "input_data": input_data,
                "form_id": user_input.form_id,
            }
        )
    return render_template(
        "edit_user_input.html", user_input=user_input, input_types=input_types
    )


@app.route("/delete_form/<int:id>", methods=["DELETE"])
def delete_user_input(id):
    user_input = UserData.query.filter_by(id=id).first()

    if user_input is None:
        return {"error": "User Input not found"}

    db.session.delete(user_input)
    db.session.commit()

    return {"Message": "User Input deleted"}


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
