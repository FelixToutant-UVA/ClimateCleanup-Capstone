"""
Routes related to products.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from ..models import Product, User, HarvestPeriod
from .. import db

product_bp = Blueprint('product_bp', __name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'website/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Display details for a specific product.
    """
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

@product_bp.route('/add-product', methods=['POST'])
@login_required
def add_product():
    """
    Add a new product.
    """
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
                # Ensure the upload directory exists
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, f"product_{current_user.id}_{filename}")
                file.save(filepath)
                # Store the relative path that can be used with url_for('static', filename=...)
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
        
        return redirect(url_for('profile_bp.profile'))

@product_bp.route('/edit-product/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    """
    Edit an existing product.
    """
    product = Product.query.get_or_404(product_id)
    
    # Check if the product belongs to the current user
    if product.user_id != current_user.id:
        flash('You do not have permission to edit this product.', category='error')
        return redirect(url_for('profile_bp.profile'))
    
    if request.method == 'POST':
        product.name = request.form.get('productName')
        product.price = float(request.form.get('productPrice'))
        product.description = request.form.get('productDescription')
        
        # Handle product image upload
        if 'productImage' in request.files:
            file = request.files['productImage']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure the upload directory exists
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, f"product_{current_user.id}_{filename}")
                file.save(filepath)
                # Store the relative path that can be used with url_for('static', filename=...)
                product.image = f"uploads/product_{current_user.id}_{filename}"
        
        db.session.commit()
        flash('Product updated successfully!', category='success')
        
        return redirect(url_for('profile_bp.profile'))

@product_bp.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """
    Delete a product.
    """
    product = Product.query.get_or_404(product_id)
    
    # Check if the product belongs to the current user
    if product.user_id != current_user.id:
        flash('You do not have permission to delete this product.', category='error')
        return redirect(url_for('profile_bp.profile'))
    
    # Delete associated harvest periods first
    HarvestPeriod.query.filter_by(product_id=product_id).delete()
    
    # Then delete the product
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', category='success')
    
    return redirect(url_for('profile_bp.profile'))

@product_bp.route('/update-harvest-calendar', methods=['POST'])
@login_required
def update_harvest_calendar():
    """
    Update the harvest calendar for a product.
    """
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        
        # Handle both single and multiple month selections
        if request.form.getlist('months'):
            selected_months = request.form.getlist('months')
        else:
            # If months come as a comma-separated string (from fetch API)
            months_str = request.form.get('months', '')
            if months_str:
                selected_months = months_str.split(',')
            else:
                selected_months = []
        
        # Validate product belongs to current user
        product = Product.query.get_or_404(product_id)
        if product.user_id != current_user.id:
            flash('You do not have permission to update this product.', category='error')
            return redirect(url_for('profile_bp.profile'))
        
        # Delete existing harvest periods for this product
        HarvestPeriod.query.filter_by(product_id=product_id).delete()
        
        # Add new harvest periods
        for month in selected_months:
            try:
                month_int = int(month)
                if 1 <= month_int <= 12:  # Validate month is between 1-12
                    harvest_period = HarvestPeriod(
                        product_id=product_id,
                        user_id=current_user.id,
                        month=month_int
                    )
                    db.session.add(harvest_period)
            except ValueError:
                continue  # Skip invalid values
        
        db.session.commit()
        flash('Harvest calendar updated successfully!', category='success')
        
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        
        return redirect(url_for('profile_bp.profile'))
