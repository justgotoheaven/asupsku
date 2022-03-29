# -*- coding: utf-8 -*-
from app import app, db # Точка входа в приложение Flask
from flask import render_template, Response, flash, request
from flask_login import login_required, current_user
from models import User # Модели и база данных
from forms import AddInspectorForm, FindInspectorForm, ChangeInspectorEmailAndPassword, DeleteInspector
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

@app.route('/admin/staff/delete_inspector/<int:id>', methods=['POST', 'GET'])
@login_required
def admin_delete_inspector(id):
    if not current_user.is_admin():
        return Response(status=403)
    delete_form = DeleteInspector()
    if request.method == 'POST' and delete_form.is_submitted():
        pass
    return render_template('jasny/admin/delete_inspector.html',
                           page_name='Удаление инспектора',
                           username=current_user.min_name(),
                           form=delete_form)


@app.route('/admin/staff/inspector/<int:id>', methods=['POST', 'GET'])
@login_required
def admin_info_inspector(id):
    if not current_user.is_admin():
        return Response(status=403)
    change_form = ChangeInspectorEmailAndPassword()
    if request.method == 'POST' and change_form.is_submitted():
        updating_data = dict()
        if change_form.email.data:
            updating_data['email'] = change_form.email.data
        if change_form.password.data:
            from werkzeug.security import generate_password_hash
            updating_data['password_hash'] = generate_password_hash(change_form.password.data)
        if updating_data:
            User.query.filter_by(id=id).update(updating_data)
            db.session.commit()
            flash('Данные пользователя изменены!')

    this_user = db.session.query(User.inspector).filter(User.id == id).first()
    if not this_user.inspector:
        return render_template('jasny/admin/show_insp_information.html',
                               page_name='Информация инспектора',
                               username=current_user.min_name(),
                               not_insp=True,
                               form=change_form)
    insp_user = db.session.query(User.login,
                           User.name,
                           User.email,
                           User.created_on,
                           User.created_by,
                           User.inspector).filter(User.id == id).first()
    who_registered = ''
    try:
        who_registered = db.session.query(User.name).filter(User.id == insp_user.created_by).first().name
    except:
        who_registered = 'Неизвестно'
    data = dict(id=id,
                name=insp_user.name,
                login=insp_user.login,
                email=insp_user.email,
                regdate=insp_user.created_on,
                regby=who_registered)
    return render_template('jasny/admin/show_insp_information.html',
                           insp = data,
                           show_data = True,
                           page_name='Информация инспектора',
                           username=current_user.min_name(),
                           form=change_form)

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
                        inspector = True,
                        created_by=current_user.id)
        user_password = generate_password(8)
        new_user.set_password(user_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Инспектор {0} создан успешно\n\nЛогин: {1}\nПароль: {2}'.format(add_form.insp_name.data,
                                                                                insp_username,
                                                                                user_password))
            return render_template('jasny/admin/add_inspector.html', page_name='Новый инспектор',
                                   username=current_user.min_name(),
                                   form=add_form)
        except Exception as e:
            db.session.rollback()
            flash('Ошибка создания пользователя<br>Техническая информация:<br>{}'.format(e))
            render_template('jasny/admin/add_inspector.html', page_name='Новый инспектор',
                            username=current_user.min_name(),
                            form=add_form)
    return render_template('jasny/admin/add_inspector.html', page_name='Новый инспектор',
                           username=current_user.min_name(),
                           form=add_form)