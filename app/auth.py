from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint('auth', __name__)


import re  # Email validation
from datetime import datetime

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    """Basit email format kontrolü"""
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(regex, email)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        # --- Input Validation ---
        if not email or not password:
            flash('Email and password are required.', category='error')
            return render_template("login.html")
        if not is_valid_email(email):
            flash('Invalid email format.', category='error')
            return render_template("login.html")

        # --- Database Query ---
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('Email does not exist.', category='error')
            # Optionally log failed attempt
            print(f"[{datetime.now()}] Failed login attempt: {email} (non-existent)")
            return render_template("login.html")

        if not check_password_hash(user.password, password):
            flash('Incorrect password, try again.', category='error')
            # Optionally log failed attempt
            print(f"[{datetime.now()}] Failed login attempt: {email} (wrong password)")
            return render_template("login.html")

        # --- Successful Login ---
        login_user(user, remember=True)

        # Optional: Log login time or track user session
        print(f"[{datetime.now()}] User logged in: {email}")

        flash('Logged in successfully!', category='success')
        return redirect(url_for('views.home'))

    return render_template("login.html")


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif not is_valid_email(email):
            flash('Invalid email format.', category='error')
            return render_template("login.html")
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 3:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("register.html", user=current_user)