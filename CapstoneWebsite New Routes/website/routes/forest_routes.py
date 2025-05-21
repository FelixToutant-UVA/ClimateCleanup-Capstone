"""
Routes related to food forests.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_
from ..models import User, CarbonData, Product, HarvestPeriod
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
            carbon_estimate = calculate_carbon_sequestration(
                carbon_data.size_m2,
                carbon_data.age_years,
                carbon_data.soil_type,
                carbon_data.biodiversity_index
            )
            
            if carbon_estimate:
                metrics['carbon'] = round((carbon_estimate['min'] + carbon_estimate['max']) / 2, 1)  # Average
        
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

@forest_bp.route('/forest/<int:forest_id>')
def forest_detail(forest_id):
    """
    Display details for a specific food forest.
    """
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
        carbon_estimate = calculate_carbon_sequestration(
            carbon_data.size_m2,
            carbon_data.age_years,
            carbon_data.soil_type,
            carbon_data.biodiversity_index
        )
        
        if carbon_estimate:
            avg_carbon = (carbon_estimate['min'] + carbon_estimate['max']) / 2
            metrics['carbon'] = f"Stores {round(avg_carbon, 1)} tons of CO₂ annually"
        
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

@forest_bp.route('/forest')
def forest():
    """
    Redirect to the first forest or show a default view.
    """
    # Redirect to the first forest or show a default view
    forest = User.query.filter_by(account_type='food-forest').first()
    if forest:
        return redirect(url_for('forest_bp.forest_detail', forest_id=forest.id))
    
    # If no forests exist, show a default view
    return render_template(
        "forest.html", 
        user=current_user,
        forest_name='Harmony Food Forest',
        forest_location='Amsterdam, Netherlands'
    )
