from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Form(db.Model):
    __tablename__ = "form"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Form {self.id}>"


input_types = [
    {"name": "Text", "value": "text"},
    {"name": "Number", "value": "number"},
    {"name": "Email", "value": "email"},
    {"name": "Password", "value": "password"},
    {"name": "Checkbox", "value": "checkbox"},
    {"name": "Radio", "value": "radio"},
    {"name": "Select", "value": "select"},
    {"name": "Textarea", "value": "textarea"},
]
