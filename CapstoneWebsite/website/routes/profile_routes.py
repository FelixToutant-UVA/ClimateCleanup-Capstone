from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user, logout_user
import os
from werkzeug.utils import secure_filename
from ..models import CarbonData, Product, HarvestPeriod, User
from .. import db
from ..utils.carbon_utils import calculate_carbon_sequestration
from ..utils.geocoding_utils import update_forest_coordinates, update_business_coordinates

profile_bp = Blueprint('profile_bp', __name__)

# Configuration for file uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile')
@login_required
def profile():
  carbon_data = CarbonData.query.filter_by(user_id=current_user.id).first()
  products = Product.query.filter_by(user_id=current_user.id).all()
  
  # Get harvest periods for each product
  product_harvest_periods = {}
  for product in products:
      harvest_periods = HarvestPeriod.query.filter_by(product_id=product.id).all()
      product_harvest_periods[product.id] = [period.month for period in harvest_periods]
  
  # Get liked forests
  from ..models import ForestLike
  liked_forest_ids = db.session.query(ForestLike.forest_id).filter_by(user_id=current_user.id).all()
  liked_forest_ids = [like[0] for like in liked_forest_ids]
  liked_forests = User.query.filter(User.id.in_(liked_forest_ids)).all() if liked_forest_ids else []
  
  # Calculate carbon estimate if data exists
  carbon_estimate = None
  if carbon_data:
      carbon_estimate = calculate_carbon_sequestration(
          carbon_data.size_m2,
          carbon_data.age_years,
          carbon_data.soil_type,
          carbon_data.biodiversity_index
      )
  
  return render_template(
      "profile.html", 
      user=current_user, 
      carbon_data=carbon_data, 
      carbon_estimate=carbon_estimate,
      products=products,
      product_harvest_periods=product_harvest_periods,
      liked_forests=liked_forests
  )

@profile_bp.route('/update-forest', methods=['POST'])
@login_required
def update_forest():
  if request.method == 'POST':
      forest_name = request.form.get('forestName')
      forest_location = request.form.get('forestLocation')
      soil_type = request.form.get('soilType')
      forest_age = request.form.get('forestAge')
      forest_size = request.form.get('forestSize')
      contact_email = request.form.get('contactEmail')
      contact_phone = request.form.get('contactPhone')
      contact_visible = request.form.get('contactVisible') == 'on'
      messages_enabled = request.form.get('messagesEnabled') == 'on'
      
      # Update user forest details
      current_user.forest_name = forest_name
      current_user.forest_location = forest_location
      current_user.contact_email = contact_email
      current_user.contact_phone = contact_phone
      current_user.contact_visible = contact_visible
      current_user.messages_enabled = messages_enabled
      current_user.account_type = 'food-forest'
      
      # Handle forest image upload
      if 'forestImage' in request.files:
          file = request.files['forestImage']
          if file and file.filename != '' and allowed_file(file.filename):
              try:
                  filename = secure_filename(file.filename)
                  # Create unique filename to avoid conflicts
                  import time
                  timestamp = str(int(time.time()))
                  filename = f"forest_{current_user.id}_{timestamp}_{filename}"
                  
                  # Use app config for upload folder
                  upload_folder = current_app.config['UPLOAD_FOLDER']
                  os.makedirs(upload_folder, exist_ok=True)

                  filepath = os.path.join(upload_folder, filename)

                  file.save(filepath)

                  current_user.forest_image = f"uploads/{filename}"
                  
                  print(f"Forest image saved successfully: {filepath}")
                  print(f"Image will be accessible at: /static/uploads/{filename}")
                  print(f"Database path: uploads/{filename}")
                  flash('Forest image uploaded successfully!', category='success')
                  
              except Exception as e:
                  print(f"Error uploading forest image: {e}")
                  flash('Error uploading image. Please try again.', category='error')
      
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
      
      try:
          db.session.commit()
          
          # Update coordinates after successful save
          if current_user.account_type == 'food-forest':
              update_forest_coordinates(current_user, db.session)
          
          flash('Forest details updated successfully!', category='success')
      except Exception as e:
          db.session.rollback()
          print(f"Database error: {e}")
          flash('Error saving changes. Please try again.', category='error')
      
      return redirect(url_for('profile_bp.profile'))

@profile_bp.route('/business-profile')
@login_required
def business_profile():
  if current_user.account_type != 'business':
      flash('Unauthorized access.', category='error')
      return redirect(url_for('profile_bp.profile'))

  # Query for food forests (users with account_type='food-forest')
  nearby_forests = User.query.filter_by(account_type='food-forest').limit(6).all()
  
  # Get carbon data for each forest
  forest_data = []
  for forest in nearby_forests:
      carbon_data = CarbonData.query.filter_by(user_id=forest.id).first()
      
      forest_data.append({
          'id': forest.id,
          'name': forest.forest_name or f"Food Forest #{forest.id}",
          'location': forest.forest_location or "Location not specified",
          'image': forest.forest_image or 'uploads/Orchard-Chickens-skylar-jean-U46bGX6KRfU-unsplash-CCO.jpg'
      })

  return render_template('business_profile.html', user=current_user, nearby_forests=forest_data)

@profile_bp.route('/update-business-about', methods=['POST'])
@login_required
def update_business_about():
  if current_user.account_type != 'business':
      flash('Unauthorized access.', category='error')
      return redirect(url_for('profile_bp.profile'))
  
  if request.method == 'POST':
      business_about = request.form.get('businessAbout')
      
      # Update the user's business_about field
      current_user.business_about = business_about
      db.session.commit()
      
      # Update coordinates if business location data exists
      if current_user.account_type == 'business':
          update_business_coordinates(current_user, db.session)
      
      flash('About section updated successfully!', category='success')
      return redirect(url_for('profile_bp.business_profile'))

@profile_bp.route('/delete-profile', methods=['POST'])
@login_required
def delete_profile():
    """
    Delete user profile and all associated data.
    """
    try:
        user_id = current_user.id
        user_email = current_user.email
        
        # Delete harvest periods
        HarvestPeriod.query.filter_by(user_id=user_id).delete()
        
        # Delete products
        Product.query.filter_by(user_id=user_id).delete()
        
        # Delete carbon data
        CarbonData.query.filter_by(user_id=user_id).delete()
        
        # Delete metrics history
        from ..models import MetricsHistory
        MetricsHistory.query.filter_by(user_id=user_id).delete()
        
        # Delete forest likes
        from ..models import ForestLike
        ForestLike.query.filter_by(user_id=user_id).delete()  
        ForestLike.query.filter_by(forest_id=user_id).delete()
        
        # Delete notes
        from ..models import Note
        Note.query.filter_by(user_id=user_id).delete()
        
        # Finally delete the user
        db.session.delete(current_user)
        
        # Commit all deletions
        db.session.commit()
        
        # Log the user out
        logout_user()
        
        flash(f'Profile for {user_email} has been permanently deleted.', category='success')
        return redirect(url_for('views.home'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting profile: {e}")
        flash('An error occurred while deleting your profile. Please try again or contact support.', category='error')
        return redirect(url_for('profile_bp.profile'))
