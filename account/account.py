# -*- coding: utf-8 -*-
from app import app # Точка входа в приложение Flask
from flask import session, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import User


@app.route('/account/settings', methods=['POST', 'GET'])
@login_required
def account_settings():
    pass