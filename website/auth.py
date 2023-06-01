from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import models
import flask_login


auth = Blueprint('auth',__name__)

@auth.route('/user/login', methods=['GET','POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = models.User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flask_login.login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('views.user_home'))
            else:
                flash('Incorrect password, try again', 'error')
        else:
            flash('Email does not exist', 'error')

    return render_template("user_login.html")

@auth.route('/user/signUp', methods = ['GET','POST'])
def user_signUp():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')

        user = models.User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash("Email is too short", category = 'error')
        elif len(first_name) < 2:
            flash("First Name is too short", category = 'error')
        elif len(password1) < 7:
            flash("Password is too short", category = 'error')
        elif password1 != password2:
            flash("Password not matching", category = "error")
        else:
            user = models.User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'), role=role)
            db.session.add(user)
            db.session.commit()
            flask_login.login_user(user)
            flash('Account Created!', category='success')
            return redirect(url_for('views.user_home'))

    return render_template("user_signUp.html")

@auth.route('/user/logout')
@flask_login.login_required
def user_logout():
    flask_login.logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.user_login'))

@auth.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = models.User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flask_login.login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('views.admin_home'))
            else:
                flash('Incorrect password, try again', 'error')
        else:
            flash('Email does not exist', 'error')

    return render_template("admin_login.html") 
    
@auth.route('/admin/signUp', methods = ['GET','POST'])
def admin_signUp():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')

        user = models.User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash("Email is too short", category = 'error')
        elif len(first_name) < 2:
            flash("First Name is too short", category = 'error')
        elif len(password1) < 7:
            flash("Password is too short", category = 'error')
        elif password1 != password2:
            flash("Password not matching", category = "error")
        else:
            user = models.User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'), role=role)
            db.session.add(user)
            db.session.commit()
            flask_login.login_user(user)
            flash('Account Created!', category='success')
            return redirect(url_for('views.admin_home'))

    return render_template("admin_signUp.html") 

@auth.route('/admin/logout')
@flask_login.login_required
def admin_logout():
    flask_login.logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.admin_login'))
