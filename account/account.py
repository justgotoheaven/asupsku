# -*- coding: utf-8 -*-
from app import app, db
from flask import render_template, request, flash
from flask_login import login_required, current_user
from forms import ChangeUserEmailForm, ChangeUserPasswordForm
from models import User
from werkzeug.security import generate_password_hash


@app.route('/account/settings', methods=['POST', 'GET'])
@login_required
def account_settings():
    if current_user.is_admin() is True:
        role = 1
    elif current_user.is_inspector() is True:
        role = 2
    else:
        role = 3
    new_pass_form = ChangeUserPasswordForm()
    new_email_form = ChangeUserEmailForm()
    if request.method == 'POST' and new_pass_form.validate_on_submit():
        updating_data = dict()
        updating_data['password_hash'] = generate_password_hash(new_pass_form.new_password.data)
        try:
            User.query.filter_by(id=current_user.id).update(updating_data)
            db.session.commit()
            flash('Ваш пароль успешно изменен', 'alert alert-success')
        except:
            db.session.rollback()
            flash('Возникла ошибка при смене пароля. Обратитесь в УК.', 'alert alert-danger')
    if request.method == 'POST' and new_email_form.validate_on_submit():
        updating_data = dict()
        updating_data['email'] = new_email_form.new_email.data
        try:
            User.query.filter_by(id=current_user.id).update(updating_data)
            db.session.commit()
            flash('Ваш email успешно изменен на {}'.format(new_email_form.new_email.data), 'alert alert-success')
        except:
            db.session.rollback()
            flash('Возникла ошибка при смене email. Обратитесь в УК.', 'alert alert-danger')
    return render_template('jasny/user/user_account_settings.html',
                           account=current_user,
                           page_name='Управление аккаунтом',
                           role=role,
                           new_pass_form=new_pass_form,
                           new_email_form=new_email_form,
                           username=current_user.min_name())