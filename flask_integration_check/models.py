# sql database class init

from flask_sqlalchemy import SQLAlchemy  #pip install flask_sqlalchemy

db = SQLAlchemy()

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(10), nullable=False)
