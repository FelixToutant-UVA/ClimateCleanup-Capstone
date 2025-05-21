# views.py
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, CarbonData, Product, User, HarvestPeriod
from . import db
import json
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_

views = Blueprint('views', __name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Main views file that imports and registers all route blueprints.
# This file is kept for backward compatibility but delegates to modular route files.
from .routes.metrics_routes import metrics_bp
from .routes.forest_routes import forest_bp
from .routes.product_routes import product_bp
from .routes.profile_routes import profile_bp
from .routes.general_routes import general_bp

# Create a main blueprint that will be registered in __init__.py
views = Blueprint('views', __name__)

# Import all the route functions to make them available
from .routes.metrics_routes import metrics, delete_carbon
from .routes.forest_routes import food_forests, forest_detail, forest
from .routes.product_routes import (
    product_detail, add_product, edit_product, 
    delete_product, update_harvest_calendar
)
from .routes.profile_routes import (
    profile, update_forest, business_profile, update_business_about
)
from .routes.general_routes import home, about_us, article, delete_note

# Register the route functions with the main blueprint
# This maintains backward compatibility with existing code

# General routes
views.add_url_rule('/', 'home', home)
views.add_url_rule('/about-us', 'about_us', about_us)
views.add_url_rule('/article', 'article', article)
views.add_url_rule('/delete-note', 'delete_note', delete_note, methods=['POST'])

# Metrics routes
views.add_url_rule('/metrics', 'metrics', metrics, methods=['GET', 'POST'])
views.add_url_rule('/delete-carbon/<int:id>', 'delete_carbon', delete_carbon, methods=['POST'])

# Forest routes
views.add_url_rule('/food-forests', 'food_forests', food_forests)
views.add_url_rule('/forest/<int:forest_id>', 'forest_detail', forest_detail)
views.add_url_rule('/forest', 'forest', forest)

# Product routes
views.add_url_rule('/product/<int:product_id>', 'product_detail', product_detail)
views.add_url_rule('/add-product', 'add_product', add_product, methods=['POST'])
views.add_url_rule('/edit-product/<int:product_id>', 'edit_product', edit_product, methods=['POST'])
views.add_url_rule('/delete-product/<int:product_id>', 'delete_product', delete_product, methods=['POST'])
views.add_url_rule('/update-harvest-calendar', 'update_harvest_calendar', update_harvest_calendar, methods=['POST'])

# Profile routes
views.add_url_rule('/profile', 'profile', profile)
views.add_url_rule('/update-forest', 'update_forest', update_forest, methods=['POST'])
views.add_url_rule('/business-profile', 'business_profile', business_profile)
views.add_url_rule('/update-business-about', 'update_business_about', update_business_about, methods=['POST'])
