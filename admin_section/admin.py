# -*- coding: utf-8 -*-
import os
import sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from app import app
from flask_login import current_user, login_required
from flask import render_template, Response

@app.route('/admin/')
@login_required
def admin_page():
    if not current_user.is_admin():
        return Response(status=403)
    return render_template('jasny/admin/index.html', page_name='Панель администратора',
                           username=current_user.min_name())