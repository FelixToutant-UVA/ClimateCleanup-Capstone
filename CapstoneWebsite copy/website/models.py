from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

    # Relationship
    carbon_data = db.relationship('CarbonData')

class CarbonData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    size_m2 = db.Column(db.Float, nullable=False)         # size in square meters
    soil_type = db.Column(db.String(100), nullable=False)
    age_years = db.Column(db.Integer, nullable=False)

    # Link to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
