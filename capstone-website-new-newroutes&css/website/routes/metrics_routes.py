"""
Routes related to metrics and carbon calculations.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import CarbonData
from .. import db
from ..utils.carbon_utils import calculate_carbon_sequestration

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

    # Calculate carbon sequestration
    carbon_estimate = None
    if carbon_data:
        carbon_estimate = calculate_carbon_sequestration(
            carbon_data.size_m2,
            carbon_data.age_years,
            carbon_data.soil_type,
            carbon_data.biodiversity_index
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

    return render_template(
        "metrics.html",
        user=current_user,
        carbon_data=carbon_data,
        carbon_estimate=carbon_estimate,
        biodiversity_index=carbon_data.biodiversity_index if carbon_data else 0.75,
        show_form=request.args.get("form")
    )

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
