from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from ..models import User, CarbonData, Product, HarvestPeriod, ForestLike, Message
from .. import db
from ..utils.carbon_utils import calculate_carbon_sequestration

forest_bp = Blueprint('forest_bp', __name__)

@forest_bp.route('/food-forests')
def food_forests():
    """
    Display list of food forests with search and filter options.
    """
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    location_filter = request.args.get('location', '')
    forest_type = request.args.get('forest_type', '')
    sort_by = request.args.get('sort_by', 'newest')
    
    # Start with base query for food forest users
    query = User.query.filter_by(account_type='food-forest')
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                User.forest_name.ilike(search),
                User.forest_location.ilike(search),
                User.products.any(Product.name.ilike(search)),
                User.products.any(Product.description.ilike(search))
            )
        )
    # Apply location filter if provided
    if location_filter:
        query = query.filter(User.forest_location.ilike(f'%{location_filter}%'))
    
    # Apply sorting
    if sort_by == 'newest':
        # Assuming newer forests have higher IDs
        query = query.order_by(User.id.desc())
    elif sort_by == 'oldest':
        query = query.order_by(User.id.asc())
    elif sort_by == 'size':
        query = query.join(CarbonData, User.id == CarbonData.user_id, isouter=True)\
                     .order_by(CarbonData.size_m2.desc())
    elif sort_by == 'biodiversity':
        query = query.join(CarbonData, User.id == CarbonData.user_id, isouter=True)\
                     .order_by(CarbonData.biodiversity_index.desc())
    
    # Add pagination logic
    page = request.args.get('page', 1, type=int)
    per_page = 12 

    # Apply pagination to the query
    forests_paginated = query.paginate(
        page=page, per_page=per_page, error_out=False
    )

    forests = forests_paginated.items
    
    # Get carbon data and coordinates for each forest
    forest_data = []
    for forest in forests:
        carbon_data = CarbonData.query.filter_by(user_id=forest.id).first()
        
        # Use actual coordinates from database if available
        coordinates = None
        if forest.forest_latitude and forest.forest_longitude:
            coordinates = (forest.forest_latitude, forest.forest_longitude)
        else:
            # Fallback to Amsterdam area with offset
            from ..utils.geocoding_utils import get_amsterdam_fallback_coordinates
            coordinates = get_amsterdam_fallback_coordinates(len(forest_data))
        
        # Calculate metrics if carbon data exists
        metrics = {}
        if carbon_data:
            metrics['species'] = int(carbon_data.biodiversity_index * 100) 
            metrics['acres'] = round(carbon_data.size_m2 / 4047, 1) 
            
            # Calculate carbon sequestration
            carbon_estimate = calculate_carbon_sequestration(
                carbon_data.size_m2,
                carbon_data.age_years,
                carbon_data.soil_type,
                carbon_data.biodiversity_index
            )
            
            if carbon_estimate:
                metrics['carbon'] = round((carbon_estimate['min'] + carbon_estimate['max']) / 2, 1) 
        
        forest_data.append({
            'id': forest.id,
            'name': forest.forest_name,
            'location': forest.forest_location,
            'image': forest.forest_image or 'uploads/Orchard-Chickens-skylar-jean-U46bGX6KRfU-unsplash-CCO.jpg',
            'metrics': metrics,
            'type': 'Community', 
            'coordinates': coordinates
        })
    
    # Get featured forest
    featured_forest = forest_data[0] if forest_data else None
    
    return render_template(
        "food_forests.html", 
        user=current_user,
        forests=forest_data,
        featured_forest=featured_forest,
        search_query=search_query,
        location_filter=location_filter,
        forest_type=forest_type,
        sort_by=sort_by,
        pagination=forests_paginated
    )

@forest_bp.route('/forest/<int:forest_id>')
def forest_detail(forest_id):
    """
    Display details for a specific food forest.
    """
    # Get the forest
    forest = User.query.filter_by(id=forest_id, account_type='food-forest').first_or_404()
    
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
        carbon_estimate = calculate_carbon_sequestration(
            carbon_data.size_m2,
            carbon_data.age_years,
            carbon_data.soil_type,
            carbon_data.biodiversity_index
        )
        
        if carbon_estimate:
            # Use the annual carbon sequestration for display
            avg_annual_carbon = (carbon_estimate['annual_min'] + carbon_estimate['annual_max']) / 2
            metrics['carbon'] = f"{round(avg_annual_carbon, 1)} tons CO₂/year"
        else:
            metrics['carbon'] = "Data not available"
        
        # Calculate biodiversity impact
        species_count = int(carbon_data.biodiversity_index * 60) 
        metrics['biodiversity'] = f"+{species_count} species supported"
        
        # Calculate water savings based on forest size and soil type
        from ..utils.carbon_utils import calculate_water_savings
        water_savings = calculate_water_savings(carbon_data.size_m2, carbon_data.age_years, carbon_data.soil_type)
        if water_savings:
            metrics['water'] = f"{water_savings['reduction_percentage']}% less water usage"
        else:
            metrics['water'] = "60% less water usage"
        
        # Soil health based on age and biodiversity
        if carbon_data.age_years >= 5 and carbon_data.biodiversity_index > 0.6:
            metrics['soil'] = "Highly Regenerative"
        elif carbon_data.age_years >= 3:
            metrics['soil'] = "Regenerative"
        else:
            metrics['soil'] = "Building Health"
            
        # Calculate water storage for display
        from ..utils.carbon_utils import calculate_water_storage
        water_stored = calculate_water_storage(carbon_data.size_m2, carbon_data.soil_type, carbon_data.age_years)
        metrics['water_stored'] = f"{water_stored:,.0f} m³"
        
    else:
        # Default values when no carbon data is available
        metrics = {
            'biodiversity': '+45 species supported',
            'carbon': '12 tons CO₂/year',
            'water': '60% less water usage',
            'soil': 'Regenerative',
            'water_stored': '3,671 m³'
        }
    
    # Calculate carbon estimate using the utility function
    carbon_estimate = None
    if carbon_data:
        carbon_estimate = calculate_carbon_sequestration(
            carbon_data.size_m2,
            carbon_data.age_years,
            carbon_data.soil_type,
            carbon_data.biodiversity_index
        )

    # If no carbon estimate calculated, provide defaults
    if not carbon_estimate:
        carbon_estimate = {
            'min': 15,
            'max': 30,
            'unit': 'tons CO₂e'
        }

    return render_template(
        "forest.html", 
        user=current_user,
        forest=forest,
        carbon_data=carbon_data,
        products=products,
        product_harvest_periods=product_harvest_periods,
        metrics=metrics,
        biodiversity_index=carbon_data.biodiversity_index if carbon_data else 0.75,
        water_stored=metrics.get('water_stored', '3,671'),
        carbon_estimate=carbon_estimate
    )

@forest_bp.route('/forest')
def forest():
    forest = User.query.filter_by(account_type='food-forest').first()
    if forest:
        return redirect(url_for('views.forest_detail', forest_id=forest.id))
    
    # If no forests exist, show a default view with some sample data
    return render_template(
        "forest.html", 
        user=current_user,
        forest=None,
        forest_name='Harmony Food Forest',
        forest_location='Amsterdam, Netherlands',
        products=[],
        product_harvest_periods={},
        metrics={
            'biodiversity': '+45 species supported',
            'carbon': '12 tons CO₂/year',
            'water': '60% less water usage',
            'soil': 'Regenerative'
        }
    )

@forest_bp.route('/api/forest/contact/<int:forest_id>')
def get_contact_info(forest_id):
    forest = User.query.filter_by(id=forest_id, account_type='food-forest').first_or_404()
    
    if not forest.contact_visible:
        return jsonify({'success': False, 'message': 'Contact information not available'})
    
    contact_data = {
        'success': True,
        'email': forest.contact_email if forest.contact_email else None,
        'phone': forest.contact_phone if forest.contact_phone else None
    }
    
    return jsonify(contact_data)

# These routes need to be accessible from the main views blueprint
def register_like_routes(app):
    @app.route('/like-forest/<int:forest_id>', methods=['POST'])
    @login_required
    def like_forest(forest_id):
        print(f"Like request received for forest {forest_id} by user {current_user.id}")
        
        forest = User.query.filter_by(id=forest_id, account_type='food-forest').first()
        if not forest:
            print(f"Forest {forest_id} not found")
            return jsonify({'success': False, 'message': 'Forest not found'}), 404
        
        existing_like = ForestLike.query.filter_by(user_id=current_user.id, forest_id=forest_id).first()
        
        try:
            if existing_like:
                db.session.delete(existing_like)
                liked = False
                print(f"Removed like for forest {forest_id}")
            else:
                new_like = ForestLike(user_id=current_user.id, forest_id=forest_id)
                db.session.add(new_like)
                liked = True
                print(f"Added like for forest {forest_id}")
            
            db.session.commit()
            
            # Get total likes count
            likes_count = ForestLike.query.filter_by(forest_id=forest_id).count()
            print(f"Total likes for forest {forest_id}: {likes_count}")
            
            return jsonify({'success': True, 'liked': liked, 'likes_count': likes_count})
            
        except Exception as e:
            db.session.rollback()
            print(f"Error toggling like: {e}")
            return jsonify({'success': False, 'message': 'Database error'}), 500

    @app.route('/like-status/<int:forest_id>')
    @login_required
    def get_like_status(forest_id):
        forest = User.query.filter_by(id=forest_id, account_type='food-forest').first()
        if not forest:
            return jsonify({'success': False, 'message': 'Forest not found'}), 404
        
        existing_like = ForestLike.query.filter_by(user_id=current_user.id, forest_id=forest_id).first()
        likes_count = ForestLike.query.filter_by(forest_id=forest_id).count()
        
        return jsonify({
            'success': True, 
            'liked': existing_like is not None,
            'likes_count': likes_count
        })

    @app.route('/send-message/<int:forest_id>', methods=['POST'])
    @login_required  
    def send_message(forest_id):
        """Send a message to a forest owner."""
        forest = User.query.filter_by(id=forest_id, account_type='food-forest').first()
        if not forest:
            return jsonify({'success': False, 'message': 'Forest not found'}), 404
        
        if not forest.messages_enabled:
            return jsonify({'success': False, 'message': 'This forest owner is not accepting messages'})
        
        data = request.get_json()
        subject = data.get('subject', '') if data else '';
        content = data.get('content', '') if data else '';
        
        if not content:
            return jsonify({'success': False, 'message': 'Message content is required'})
        
        message = Message(
            sender_id=current_user.id,
            recipient_id=forest_id,
            subject=subject,
            content=content
        )
        
        try:
            db.session.add(message)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Message sent successfully'})
        except Exception as e:
            db.session.rollback()
            print(f"Error sending message: {e}")
            return jsonify({'success': False, 'message': 'Database error'}), 500
