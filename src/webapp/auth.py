from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from . import db
from .data_models import User


auth = Blueprint('auth', __name__)


@auth.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash(f'Hello there, {user.username}', category='success')
                login_user(user, remember=remember)

                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("authentication/sign_in.html",
                           user=current_user,
                           active_page='sign_in')


@auth.route('/sign_out')
@login_required
def sign_out():
    logout_user()

    return redirect(url_for('views.home'))


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        # check user input is valid
        if email_exists:
            flash('Email already exists.', category='error')
        elif username_exists:
            flash('Username already exists', category='error')
        elif len(username) < 2:
            flash('Username cannot be 1 character', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 5:
            flash('Password must at least 6 characters long.', category='error')
        else:
            # add new user to db
            new_user = User(email=email, username=username, password=generate_password_hash(password1), creation_date=datetime.today().date())
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            flash(f'Welcome, {username}!', category='success')

            return redirect(url_for('views.home'))

    return render_template("authentication/sign_up.html",
                           user=current_user,
                           active_page='sign_up')