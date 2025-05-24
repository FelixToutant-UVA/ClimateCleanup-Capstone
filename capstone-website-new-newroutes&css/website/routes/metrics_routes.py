"""
Routes related to metrics and carbon calculations.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ..models import CarbonData, MetricsHistory
from .. import db
from ..utils.carbon_utils import calculate_carbon_sequestration, calculate_water_storage
from datetime import datetime, timedelta
import json

metrics_bp = Blueprint('metrics_bp', __name__)

@metrics_bp.route('/metrics', methods=['GET', 'POST'])
@login_required
def metrics():
    """
    Handle metrics page - display and update carbon data.
    """
    carbon_data = CarbonData.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        size = request.form.get('size')
        soil = request.form.get('soil')
        age = request.form.get('age')
        biodiversity_index = request.form.get('biodiversity_index', 0.75)

        # Calculate derived values
        carbon_estimate = calculate_carbon_sequestration(
            float(size), int(age), soil, float(biodiversity_index)
        )
        water_stored = calculate_water_storage(float(size), soil, int(age))
        
        # Calculate average carbon sequestration for storage
        avg_carbon = 0
        if carbon_estimate:
            avg_carbon = (carbon_estimate['min'] + carbon_estimate['max']) / 2

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

        # Store historical data
        metrics_entry = MetricsHistory(
            user_id=current_user.id,
            size_m2=float(size),
            soil_type=soil,
            age_years=int(age),
            biodiversity_index=float(biodiversity_index),
            carbon_sequestration=avg_carbon,
            water_stored=water_stored,
            date_recorded=datetime.now()
        )
        db.session.add(metrics_entry)

        db.session.commit()
        return redirect(url_for('views.metrics'))

    # Get historical data for charts
    historical_data = MetricsHistory.query.filter_by(user_id=current_user.id)\
                                         .order_by(MetricsHistory.date_recorded.asc())\
                                         .all()

    # Calculate current carbon sequestration
    carbon_estimate = None
    water_stored = 0
    if carbon_data:
        carbon_estimate = calculate_carbon_sequestration(
            carbon_data.size_m2,
            carbon_data.age_years,
            carbon_data.soil_type,
            carbon_data.biodiversity_index
        )
        water_stored = calculate_water_storage(
            carbon_data.size_m2, 
            carbon_data.soil_type, 
            carbon_data.age_years
        )
    else:
        # Provide default values when carbon_data is None
        carbon_estimate = {
            "min": 15,
            "max": 30,
            "unit": "tons CO₂e",
            "annual_min": 2.1,
            "annual_max": 4.2,
            "annual_unit": "tons CO₂e/year"
        }
        water_stored = 3671

    return render_template(
        "metrics.html",
        user=current_user,
        carbon_data=carbon_data,
        carbon_estimate=carbon_estimate,
        biodiversity_index=carbon_data.biodiversity_index if carbon_data else 0.75,
        water_stored=f"{water_stored:,.0f}",
        historical_data=historical_data,
        show_form=request.args.get("form")
    )

@metrics_bp.route('/api/metrics-data')
@login_required
def get_metrics_data():
    """
    API endpoint to get historical metrics data for charts.
    """
    # Get time range from query parameters
    days = request.args.get('days', 365, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    historical_data = MetricsHistory.query.filter(
        MetricsHistory.user_id == current_user.id,
        MetricsHistory.date_recorded >= start_date
    ).order_by(MetricsHistory.date_recorded.asc()).all()
    
    # Format data for charts
    chart_data = {
        'labels': [],
        'carbon_data': [],
        'water_data': [],
        'biodiversity_data': [],
        'size_data': []
    }
    
    for entry in historical_data:
        chart_data['labels'].append(entry.date_recorded.strftime('%Y-%m-%d'))
        chart_data['carbon_data'].append(entry.carbon_sequestration or 0)
        chart_data['water_data'].append(entry.water_stored or 0)
        chart_data['biodiversity_data'].append(entry.biodiversity_index or 0)
        chart_data['size_data'].append(entry.size_m2 / 10000 if entry.size_m2 else 0)  # Convert to hectares
    
    return jsonify(chart_data)

@metrics_bp.route('/delete-carbon/<int:id>', methods=['POST'])
@login_required
def delete_carbon(id):
    """
    Delete carbon data entry.
    """
    carbon = CarbonData.query.get_or_404(id)

    if carbon.user_id != current_user.id:
        flash("Not authorized to delete this", category="error")
        return redirect(url_for('views.metrics'))

    db.session.delete(carbon)
    db.session.commit()
    flash("Carbon data deleted.", category="success")
    return redirect(url_for('views.metrics'))
