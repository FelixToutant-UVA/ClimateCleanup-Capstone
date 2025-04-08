from .models import CarbonData
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json

views = Blueprint('views', __name__)

# Soil, Size and Age of food-forests
# Soil sequestration rates: tons CO2e per hectare per year
SEQUESTRATION_RATES = {
    "Grassland": (3.74, 9.84),
    "Temperate agroforest": (14.5, 14.5),
    "Mature forest (reforested)": (10, 20),
    "Peatland (restored)": (25, 30)
}

@views.route('/metrics', methods=['GET', 'POST'])
@login_required
def metrics():
    carbon_data = CarbonData.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        size = request.form.get('size')
        soil = request.form.get('soil')
        age = request.form.get('age')

        if carbon_data:
            # Edit existing
            carbon_data.size_m2 = float(size)
            carbon_data.soil_type = soil
            carbon_data.age_years = int(age)
            flash("Carbon data updated!", category='success')
        else:
            # Add new
            carbon_data = CarbonData(
                size_m2=float(size),
                soil_type=soil,
                age_years=int(age),
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



# 🌍 New EcoLink pages
@views.route('/')
def home():
    return render_template("index.html", user=current_user)

@views.route('/about-us')
def about_us():
    return render_template("about_us.html", user=current_user)

@views.route('/food-forests')
def food_forests():
    return render_template("food_forests.html", user=current_user)

@views.route('/profile')
def profile():
    return render_template("profile.html", user=current_user)

@views.route('/forest')
def forest():
    return render_template("forest.html", user=current_user)

@views.route('/profile')
def forest_profile():
    return render_template("profile.html", user=current_user)


