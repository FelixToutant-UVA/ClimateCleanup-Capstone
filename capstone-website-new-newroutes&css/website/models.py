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
    
    # Account type: either 'business' or 'food-forest'
    account_type = db.Column(db.String(20), default='business')

    # Business-specific fields
    business_name = db.Column(db.String(150))
    business_location = db.Column(db.String(150))
    business_about = db.Column(db.Text)

    # Food-Forest-specific fields
    forest_name = db.Column(db.String(150))
    forest_location = db.Column(db.String(150))
    forest_image = db.Column(db.String(255))  # Path to forest image
    contact_email = db.Column(db.String(150))  # Contact email for customers
    contact_phone = db.Column(db.String(50))   # Contact phone for customers
    contact_visible = db.Column(db.Boolean, default=True)  # Whether to show contact info

    # Relationships
    notes = db.relationship('Note', backref='user', lazy=True)
    carbon_data = db.relationship('CarbonData', backref='user', uselist=False)
    products = db.relationship('Product', backref='user', lazy=True)
    harvest_periods = db.relationship('HarvestPeriod', backref='user', lazy=True)
    metrics_history = db.relationship('MetricsHistory', backref='user', lazy=True)


class CarbonData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size_m2 = db.Column(db.Float)
    soil_type = db.Column(db.String(100))
    age_years = db.Column(db.Integer)
    biodiversity_index = db.Column(db.Float, default=0.75)
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))  # Path to product image
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    harvest_periods = db.relationship('HarvestPeriod', backref='product', lazy=True)

class HarvestPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12 for Jan-Dec
    date_added = db.Column(db.DateTime(timezone=True), default=func.now())

class MetricsHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    size_m2 = db.Column(db.Float)
    soil_type = db.Column(db.String(100))
    age_years = db.Column(db.Integer)
    biodiversity_index = db.Column(db.Float, default=0.75)
    carbon_sequestration = db.Column(db.Float)  # Calculated value
    water_stored = db.Column(db.Float)  # Calculated value
    date_recorded = db.Column(db.DateTime(timezone=True), default=func.now())

