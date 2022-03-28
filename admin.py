# -*- coding: utf-8 -*-
from app import app, db # Точка входа в приложение Flask
from flask import render_template, Response, flash, request
from flask_login import login_required, current_user
from models import User # Модели и база данных
from forms import AddInspectorForm, FindInspectorForm
from transliterate import translit
from random import randint
from utils import generate_password

@app.route('/admin/')
@login_required
def admin_page():
    if not current_user.is_admin():
        return Response(status=403)
    return render_template('jasny/admin/index.html', page_name='Панель администратора',
                           username=current_user.min_name())

# Раздел работы с пользователями
@app.route('/admin/staff/inspectors', methods=['POST','GET'])
@login_required
def admin_staff_page():
    if not current_user.is_admin():
        return Response(status=403)
    find_form = FindInspectorForm()
    if find_form.validate_on_submit() and request.method == 'POST':
        find_name = find_form.name.data
        find_result = User.query.filter(User.name.ilike('%{}%'.format(find_name)), User.inspector == True).all()
        if not find_result:
            return render_template('jasny/admin/show_inspector.html',
                                   form=find_form,
                                   no_result=True,
                                   page_name='Инспекторы',
                                   username=current_user.min_name())
        inspectors = list()
        for i in find_result:
            current = dict(id=i.id, name=i.name)
            inspectors.append(current)
        return render_template('jasny/admin/show_inspector.html',
                               form = find_form,
                               show_result = True,
                               data = inspectors,
                               page_name = 'Инспекторы',
                               username = current_user.min_name())
    return render_template('jasny/admin/show_inspector.html',
                           form=find_form,
                           page_name='Инспекторы',
                           username = current_user.min_name())


@app.route('/admin/staff/inspector/<int:id>', methods=['POST', 'GET'])
@login_required
def admin_info_inspector(id):
    if not current_user.is_admin():
        return Response(status=403)
    return Response(status=501)

@app.route('/admin/staff/add_inspector', methods=['POST', 'GET'])
@login_required
def admin_add_inspector():
    if not current_user.is_admin():
        return Response(status=403)
    add_form = AddInspectorForm()
    if add_form.validate_on_submit():
        username_string = '{}_{}'.format(add_form.insp_name.data.split(' ')[0], randint(100,999))
        insp_username = translit(username_string,
                                 language_code='ru',
                                 reversed=True)
        new_user = User(name = add_form.insp_name.data,
                        login = insp_username,
                        email = add_form.insp_email.data,
                        inspector = True)
        user_password = generate_password(8)
        new_user.set_password(user_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Инспектор {} создан успешно\n\nЛогин: {}\nПароль: {}'.format(add_form.insp_name.data,
                                                                                insp_username,
                                                                                user_password))
            return render_template('jasny/admin/add_inspector.html', page_name='Новый инспектор',
                                   username=current_user.min_name(),
                                   form=add_form)
        except Exception as e:
            db.session.rollback()
            flash('Ошибка создания пользователя<br>Техническая информация:<br>{}'.format(e))
            render_template('jasny/add_inspector.html', page_name='Новый инспектор',
                            username=current_user.min_name(),
                            form=add_form)
    return render_template('jasny/admin/add_inspector.html', page_name='Новый инспектор',
                           username=current_user.min_name(),
                           form=add_form)

