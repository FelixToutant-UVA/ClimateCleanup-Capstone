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

# Soil, Size and Age of food-forests
# Soil sequestration rates: tons CO2e per hectare per year
SEQUESTRATION_RATES = {
    "Zandgrond": (3.74, 9.84),
    "Kleigrond": (14.5, 14.5),
    "Veengrond": (25, 30),
    "Loess": (10, 20)
}

@views.route('/metrics', methods=['GET', 'POST'])
@login_required
def metrics():
    carbon_data = CarbonData.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        size = request.form.get('size')
        soil = request.form.get('soil')
        age = request.form.get('age')
        biodiversity_index = request.form.get('biodiversity_index', 0.75)

        if carbon_data:
            # Edit existing
            carbon_data.size_m2 = float(size)
            carbon_data.soil_type = soil
            carbon_data.age_years = int(age)
            carbon_data.biodiversity_index = float(biodiversity_index)
            flash("Carbon data updated!", category='success')
        else:
            # Add new
            carbon_data = CarbonData(
                size_m2=float(size),
                soil_type=soil,
                age_years=int(age),
                biodiversity_index=float(biodiversity_index),
                user_id=current_user.id
            )
            db.session.add(carbon_data)
            flash("Carbon data added!", category='success')

        db.session.commit()
        return redirect(url_for('views.metrics'))

    # 🧮 Carbon sequestration calculation
    carbon_estimate = None
    if carbon_data:
        area_ha = carbon_data.size_m2 / 10000
        age = carbon_data.age_years
        soil = carbon_data.soil_type

        if soil in SEQUESTRATION_RATES:
            rate_min, rate_max = SEQUESTRATION_RATES[soil]
            min_seq = round(area_ha * rate_min * age, 2)
            max_seq = round(area_ha * rate_max * age, 2)

            carbon_estimate = {
                "min": min_seq,
                "max": max_seq,
                "unit": "tons CO₂e"
            }

    return render_template(
        "metrics.html",
        user=current_user,
        carbon_data=carbon_data,
        carbon_estimate=carbon_estimate,
        biodiversity_index=carbon_data.biodiversity_index if carbon_data else 0.75,
        show_form=request.args.get("form")
    )


@views.route('/delete-carbon/<int:id>', methods=['POST'])
@login_required
def delete_carbon(id):
    carbon = CarbonData.query.get_or_404(id)

    if carbon.user_id != current_user.id:
        flash("Not authorized to delete this", category="error")
        return redirect(url_for('views.metrics'))

    db.session.delete(carbon)
    db.session.commit()
    flash("Carbon data deleted.", category="success")
    return redirect(url_for('views.metrics'))


# 🌍 EcoLink pages
@views.route('/')
def home():
    return render_template("index.html", user=current_user)

@views.route('/about-us')
def about_us():
    return render_template("about_us.html", user=current_user)

@views.route('/food-forests')
def food_forests():
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    location_filter = request.args.get('location', '')
    forest_type = request.args.get('forest_type', '')
    sort_by = request.args.get('sort_by', 'newest')
    
    # Start with base query for food forest users
    query = User.query.filter_by(account_type='food-forest')
    
    # Apply search if provided
    if search_query:
        query = query.filter(
            or_(
                User.forest_name.ilike(f'%{search_query}%'),
                User.forest_location.ilike(f'%{search_query}%')
            )
        )
    
    # Apply location filter if provided
    if location_filter:
        query = query.filter(User.forest_location.ilike(f'%{location_filter}%'))
    
    # (Optional) Apply forest type filter if you had a field like `forest_type` on the model

    # Apply sorting
    if sort_by == 'newest':
        # Assuming newer forests have higher IDs
        query = query.order_by(User.id.desc())
    elif sort_by == 'oldest':
        query = query.order_by(User.id.asc())
    elif sort_by == 'size':
        # Join with carbon_data to sort by size
        query = query.join(CarbonData, User.id == CarbonData.user_id, isouter=True)\
                     .order_by(CarbonData.size_m2.desc())
    elif sort_by == 'biodiversity':
        # Join with carbon_data to sort by biodiversity_index
        query = query.join(CarbonData, User.id == CarbonData.user_id, isouter=True)\
                     .order_by(CarbonData.biodiversity_index.desc())
    
    # Execute query
    forests = query.all()
    
    # Get carbon data for each forest
    forest_data = []
    for forest in forests:
        carbon_data = CarbonData.query.filter_by(user_id=forest.id).first()
        
        # Calculate metrics if carbon data exists
        metrics = {}
        if carbon_data:
            metrics['species'] = int(carbon_data.biodiversity_index * 100)  # Approx. number of species
            metrics['acres'] = round(carbon_data.size_m2 / 4047, 1)  # Convert m² to acres
            
            # Calculate carbon sequestration
            if carbon_data.soil_type in SEQUESTRATION_RATES:
                area_ha = carbon_data.size_m2 / 10000
                age = carbon_data.age_years
                rate_min, rate_max = SEQUESTRATION_RATES[carbon_data.soil_type]
                metrics['carbon'] = round(
                    (area_ha * rate_min * age + area_ha * rate_max * age) / 2,
                    1
                )  # Average
        
        forest_data.append({
            'id': forest.id,
            'name': forest.forest_name,
            'location': forest.forest_location,
            'image': forest.forest_image or 'images/hero_pears.jpg',
            'metrics': metrics,
            'type': 'Community'  # Example placeholder
        })
    
    # Get featured forest (first one or None)
    featured_forest = forest_data[0] if forest_data else None
    
    return render_template(
        "food_forests.html", 
        user=current_user,
        forests=forest_data,
        featured_forest=featured_forest,
        search_query=search_query,
        location_filter=location_filter,
        forest_type=forest_type,
        sort_by=sort_by
    )

@views.route('/profile')
@login_required
def profile():
    carbon_data = CarbonData.query.filter_by(user_id=current_user.id).first()
    products = Product.query.filter_by(user_id=current_user.id).all()
    
    # Get harvest periods for each product
    product_harvest_periods = {}
    for product in products:
        harvest_periods = HarvestPeriod.query.filter_by(product_id=product.id).all()
        product_harvest_periods[product.id] = [period.month for period in harvest_periods]
    
    # Calculate carbon estimate if data exists
    carbon_estimate = None
    if carbon_data:
        area_ha = carbon_data.size_m2 / 10000
        age = carbon_data.age_years
        soil = carbon_data.soil_type

        if soil in SEQUESTRATION_RATES:
            rate_min, rate_max = SEQUESTRATION_RATES[soil]
            min_seq = round(area_ha * rate_min * age, 2)
            max_seq = round(area_ha * rate_max * age, 2)

            carbon_estimate = {
                "min": min_seq,
                "max": max_seq,
                "unit": "tons CO₂e"
            }
    
    return render_template(
        "profile.html", 
        user=current_user, 
        carbon_data=carbon_data, 
        carbon_estimate=carbon_estimate,
        products=products,
        product_harvest_periods=product_harvest_periods
    )

@views.route('/update-forest', methods=['POST'])
@login_required
def update_forest():
    if request.method == 'POST':
        forest_name = request.form.get('forestName')
        forest_location = request.form.get('forestLocation')
        soil_type = request.form.get('soilType')
        forest_age = request.form.get('forestAge')
        forest_size = request.form.get('forestSize')
        
        # Update user forest details
        current_user.forest_name = forest_name
        current_user.forest_location = forest_location
        # Force account type to 'food-forest' here if you're sure this update is for a forest
        current_user.account_type = 'food-forest'
        
        # Handle forest image upload
        if 'forestImage' in request.files:
            file = request.files['forestImage']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, f"forest_{current_user.id}_{filename}")
                file.save(filepath)
                current_user.forest_image = f"uploads/forest_{current_user.id}_{filename}"
        
        # Update or create carbon data
        carbon_data = CarbonData.query.filter_by(user_id=current_user.id).first()
        if carbon_data:
            carbon_data.soil_type = soil_type
            carbon_data.age_years = int(forest_age)
            carbon_data.size_m2 = float(forest_size)
        else:
            carbon_data = CarbonData(
                soil_type=soil_type,
                age_years=int(forest_age),
                size_m2=float(forest_size),
                user_id=current_user.id
            )
            db.session.add(carbon_data)
        
        db.session.commit()
        flash('Forest details updated successfully!', category='success')
        
        return redirect(url_for('views.profile'))

@views.route('/add-product', methods=['POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('productName')
        price = request.form.get('productPrice')
        description = request.form.get('productDescription')
        
        # Create new product
        new_product = Product(
            name=name,
            price=float(price),
            description=description,
            user_id=current_user.id
        )
        
        # Handle product image upload
        if 'productImage' in request.files:
            file = request.files['productImage']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, f"product_{current_user.id}_{filename}")
                file.save(filepath)
                new_product.image = f"uploads/product_{current_user.id}_{filename}"
        
        db.session.add(new_product)
        db.session.commit()
        
        # Add default harvest periods (e.g., summer months)
        default_months = [6, 7, 8]  # June, July, August
        for month in default_months:
            harvest_period = HarvestPeriod(
                product_id=new_product.id,
                user_id=current_user.id,
                month=month
            )
            db.session.add(harvest_period)
        
        db.session.commit()
        flash('Product added successfully!', category='success')
        
        return redirect(url_for('views.profile'))

@views.route('/edit-product/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if the product belongs to the current user
    if product.user_id != current_user.id:
        flash('You do not have permission to edit this product.', category='error')
        return redirect(url_for('views.profile'))
    
    if request.method == 'POST':
        product.name = request.form.get('productName')
        product.price = float(request.form.get('productPrice'))
        product.description = request.form.get('productDescription')
        
        # Handle product image upload
        if 'productImage' in request.files:
            file = request.files['productImage']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, f"product_{current_user.id}_{filename}")
                file.save(filepath)
                product.image = f"uploads/product_{current_user.id}_{filename}"
        
        db.session.commit()
        flash('Product updated successfully!', category='success')
        
        return redirect(url_for('views.profile'))

@views.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if the product belongs to the current user
    if product.user_id != current_user.id:
        flash('You do not have permission to delete this product.', category='error')
        return redirect(url_for('views.profile'))
    
    # Delete associated harvest periods first
    HarvestPeriod.query.filter_by(product_id=product_id).delete()
    
    # Then delete the product
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', category='success')
    
    return redirect(url_for('views.profile'))

@views.route('/update-harvest-calendar', methods=['POST'])
@login_required
def update_harvest_calendar():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        selected_months = request.form.getlist('months')
        
        # Validate product belongs to current user
        product = Product.query.get_or_404(product_id)
        if product.user_id != current_user.id:
            flash('You do not have permission to update this product.', category='error')
            return redirect(url_for('views.profile'))
        
        # Delete existing harvest periods for this product
        HarvestPeriod.query.filter_by(product_id=product_id).delete()
        
        # Add new harvest periods
        for month in selected_months:
            harvest_period = HarvestPeriod(
                product_id=product_id,
                user_id=current_user.id,
                month=int(month)
            )
            db.session.add(harvest_period)
        
        db.session.commit()
        flash('Harvest calendar updated successfully!', category='success')
        
        return redirect(url_for('views.profile'))

@views.route('/forest/<int:forest_id>')
def forest_detail(forest_id):
    # Get the forest (user with account_type='food-forest')
    forest = User.query.filter_by(id=forest_id, account_type='food-forest').first_or_404()
    
    # Get carbon data
    carbon_data = CarbonData.query.filter_by(user_id=forest.id).first()
    
    # Get products
    products = Product.query.filter_by(user_id=forest.id).all()
    
    # Get harvest periods for each product
    product_harvest_periods = {}
    for product in products:
        harvest_periods = HarvestPeriod.query.filter_by(product_id=product.id).all()
        product_harvest_periods[product.id] = [period.month for period in harvest_periods]
    
    # Calculate metrics if carbon_data exists
    metrics = {}
    if carbon_data:
        metrics['biodiversity'] = f"+{int(carbon_data.biodiversity_index * 100)}% more species"
        
        # Calculate carbon sequestration
        if carbon_data.soil_type in SEQUESTRATION_RATES:
            area_ha = carbon_data.size_m2 / 10000
            age = carbon_data.age_years
            rate_min, rate_max = SEQUESTRATION_RATES[carbon_data.soil_type]
            metrics['carbon'] = f"Stores {round((area_ha * rate_min * age + area_ha * rate_max * age) / 2, 1)} tons of CO₂ annually"
        
        # Example placeholder for water conservation
        metrics['water'] = "Uses 60% less water than conventional farming"
    
    return render_template(
        "forest.html", 
        user=current_user,
        forest=forest,
        carbon_data=carbon_data,
        products=products,
        product_harvest_periods=product_harvest_periods,
        metrics=metrics
    )

@views.route('/forest')
def forest():
    # Redirect to the first forest or show a default view
    forest = User.query.filter_by(account_type='food-forest').first()
    if forest:
        return redirect(url_for('views.forest_detail', forest_id=forest.id))
    
    # If no forests exist, show a default view
    return render_template(
        "forest.html", 
        user=current_user,
        forest_name='Harmony Food Forest',
        forest_location='Amsterdam, Netherlands'
    )

# New routes for product detail and article pages
@views.route('/product/<int:product_id>')
def product_detail(product_id):
    # Get the product
    product = Product.query.get_or_404(product_id)
    
    # Get the forest (user)
    forest = User.query.get_or_404(product.user_id)
    
    # Get harvest periods for this product
    harvest_periods = HarvestPeriod.query.filter_by(product_id=product.id).all()
    harvest_months = [period.month for period in harvest_periods]
    
    return render_template(
        "product_detail.html", 
        user=current_user,
        product=product,
        forest=forest,
        harvest_months=harvest_months
    )

@views.route('/article')
def article():
    return render_template("article.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})


@views.route('/business-profile')
@login_required
def business_profile():
    if current_user.account_type != 'business':
        flash('Unauthorized access.', category='error')
        return redirect(url_for('views.profile'))


    return render_template('business_profile.html', user=current_user)
