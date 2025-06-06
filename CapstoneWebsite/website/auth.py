from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        account_type = request.form.get('account_type', 'business')

        user = User.query.filter_by(email=email, account_type=account_type).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)

                # Redirect based on account_type
                if user.account_type == 'business':
                    return redirect(url_for('views.business_profile'))
                else:
                    return redirect(url_for('views.profile'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist for this account type.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        account_type = request.form.get('account_type', 'business')

        # Get account-specific fields
        if account_type == 'business':
            business_name = request.form.get('businessName')
            business_address = request.form.get('businessAddress')
            business_city = request.form.get('businessCity') 
            business_postal_code = request.form.get('businessPostalCode')
            business_country = request.form.get('businessCountry')
        else:  # food-forest
            forest_name = request.form.get('forestName')
            forest_address = request.form.get('forestAddress')
            forest_city = request.form.get('forestCity')
            forest_postal_code = request.form.get('forestPostalCode')
            forest_country = request.form.get('forestCountry')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                account_type=account_type
            )
            
            # Set account-specific fields
            if account_type == 'business':
                new_user.business_name = business_name
                new_user.business_address = business_address
                new_user.business_city = business_city
                new_user.business_postal_code = business_postal_code
                new_user.business_country = business_country
                # Combine for backward compatibility
                new_user.business_location = f"{business_city}, {business_country}" if business_city and business_country else ""
            else:  # food-forest
                new_user.forest_name = forest_name
                new_user.forest_address = forest_address
                new_user.forest_city = forest_city
                new_user.forest_postal_code = forest_postal_code
                new_user.forest_country = forest_country
                # Combine for backward compatibility
                new_user.forest_location = f"{forest_city}, {forest_country}" if forest_city and forest_country else ""
            
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            flash('Account created!', category='success')

            # Redirect based on account_type
            if new_user.account_type == 'business':
                return redirect(url_for('views.business_profile'))
            else:
                return redirect(url_for('views.profile'))

    return render_template("sign_up.html", user=current_user)
