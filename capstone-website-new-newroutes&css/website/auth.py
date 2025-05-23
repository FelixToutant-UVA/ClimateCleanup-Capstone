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
            business_location = request.form.get('businessLocation')
        else:  # food-forest
            forest_name = request.form.get('forestName')
            forest_location = request.form.get('forestLocation')

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
                new_user.business_location = business_location
            else:  # food-forest
                new_user.forest_name = forest_name
                new_user.forest_location = forest_location
            
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
