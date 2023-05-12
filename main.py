from models import input_types, Form, db, UserData
from flask import Flask, render_template, request, redirect, url_for, jsonify, json
from datetime import datetime
from config import settings
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}"
    f"/{settings.database_name}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


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


@app.route("/<int:id>", methods=["GET"])
def get_form(id):
    form = Form.query.filter_by(id=id).first()
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


# @app.route("/<int:id>")
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


@app.route("/edit_form/<int:form_id>", methods=["GET", "PUT"])
def edit_form(form_id):
    form = Form.query.get(form_id)

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
        existing_form = Form.query.filter_by(slug=slug).first()

        if existing_form:
            return {"error": f"A form with the slug: {slug} already exists."}

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


@app.route("/delete_form/<int:form_id>", methods=["DELETE"])
def delete_form(form_id):
    form = Form.query.get(form_id)

    if form is None:
        return {"error": "Form not found"}
    db.session.delete(form)
    db.session.commit()

    return {"Message": "Form deleted"}


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
