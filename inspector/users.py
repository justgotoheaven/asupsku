from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import House, Address, Counter, User, Categories
from forms import FindUserForm


@app.route('/inspector/users', methods=['POST', 'GET'])
@login_required
def inspector_users_main():
    if not current_user.is_inspector():
        return Response(status=403)
    find_form = FindUserForm()
    if find_form.validate_on_submit() and request.method == 'POST':
        find_name = find_form.name.data
        find_result = User.query.filter(User.name.ilike('%{}%'.format(find_name))).all()
        if not find_result:
            return render_template('jasny/inspector/show_user.html',
                                   form=find_form,
                                   no_result=True,
                                   page_name='Пользователи',
                                   username=current_user.min_name())
        users = list()
        for i in find_result:
            current = dict(id=i.id, name=i.name)
            users.append(current)
        return render_template('jasny/inspector/show_user.html',
                               form=find_form,
                               show_result=True,
                               data=users,
                               page_name='Пользователи',
                               username=current_user.min_name())
    return render_template('jasny/inspector/show_user.html',
                           form=find_form,
                           page_name='Пользователи',
                           username=current_user.min_name())
