import os
import sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from app import app, db
from models import User,Categories
from flask_login import login_required, current_user
from flask import Response

@app.route('/admin/categories')
@login_required
def admin_categories_index():
    if not current_user.is_admin():
        return Response(status=403)
