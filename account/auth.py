# -*- coding: utf-8 -*-
import os
import sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from app import app, db
from flask import session, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from forms import LoginForm
from models import User
from admin_section.admin import admin_page

login_manager = LoginManager(app) # Менеджер
login_manager.login_view = 'account_login' # Функция обработки страницы входа
login_manager.login_message = '' # Сообщение входа

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

@app.route('/account/login', methods=['POST', 'GET'])
def account_login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('app_main'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.is_admin():
                return redirect(url_for('admin_page'))
            else:
                return redirect(url_for('app_main'))
        else:
            flash('Вы ввели неправильный логин или пароль. Попробуйте еще раз.')
    return render_template('login_new.html', page_name='Авторизация',
                           form=form)

@app.route('/account/logout', methods=['POST', 'GET'])
@login_required
def account_logout():
    logout_user()
    session.pop('name', None)
    return redirect(url_for('account_login'))