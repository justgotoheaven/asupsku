import os
import sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from app import app
from flask import Response, render_template
from flask_login import login_required, current_user


@app.route('/inspector')
@login_required
def inspector_index():
    if not current_user.is_inspector():
        return Response(status=403)
    return render_template('jasny/inspector/index.html',
                           page_name='Панель инспектора',
                           username=current_user.min_name())