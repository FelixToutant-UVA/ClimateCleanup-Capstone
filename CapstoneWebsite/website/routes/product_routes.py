from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from ..models import Product, User, HarvestPeriod
from .. import db

product_bp = Blueprint('product_bp', __name__)

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/product/<int:product_id>')
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

@product_bp.route('/add-product', methods=['POST'])
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
                try:
                    filename = secure_filename(file.filename)
                    # Create unique filename to avoid conflicts
                    import time
                    timestamp = str(int(time.time()))
                    filename = f"product_{current_user.id}_{timestamp}_{filename}"
                    
                    # Use app config for upload folder
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)

                    filepath = os.path.join(upload_folder, filename)

                    file.save(filepath)
                    
                    new_product.image = f"uploads/{filename}"
                    
                    print(f"Product image saved successfully: {filepath}")
                    print(f"Image will be accessible at: /static/uploads/{filename}")
                    print(f"Database path: uploads/{filename}")
                    
                except Exception as e:
                    print(f"Error uploading product image: {e}")
                    flash('Error uploading image, but product was created.', category='warning')
        
        db.session.add(new_product)
        db.session.commit()
        
        # Add default harvest periods (e.g., summer months)
        default_months = [6, 7, 8] 
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
                try:
                    filename = secure_filename(file.filename)
                    import time
                    timestamp = str(int(time.time()))
                    filename = f"product_{current_user.id}_{timestamp}_{filename}"
                    
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    os.makedirs(upload_folder, exist_ok=True)

                    filepath = os.path.join(upload_folder, filename)

                    file.save(filepath)

                    product.image = f"uploads/{filename}"
                    
                    print(f"Product image updated successfully: {filepath}")
                    print(f"Image will be accessible at: /static/uploads/{filename}")
                    print(f"Database path: uploads/{filename}")
                    
                except Exception as e:
                    print(f"Error uploading product image: {e}")
                    flash('Error uploading image, but product was updated.', category='warning')
        
        db.session.commit()
        flash('Product updated successfully!', category='success')
        
        return redirect(url_for('profile_bp.profile'))

@product_bp.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
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
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        
        # Handle both single and multiple month selections
        if request.form.getlist('months'):
            selected_months = request.form.getlist('months')
        else:
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
                if 1 <= month_int <= 12:
                    harvest_period = HarvestPeriod(
                        product_id=product_id,
                        user_id=current_user.id,
                        month=month_int
                    )
                    db.session.add(harvest_period)
            except ValueError:
                continue  
        
        db.session.commit()
        flash('Harvest calendar updated successfully!', category='success')
        
        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        
        return redirect(url_for('profile_bp.profile'))

@product_bp.route('/products')
@login_required
def products():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template("products.html", user=current_user, products=products)
