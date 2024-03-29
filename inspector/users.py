from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import User, Address
from forms import FindUserForm, AddUserForm, ChangeUserEmailAndPassword
import string
from utils import generate_password
from transliterate import translit
from random import randint
from mailer import send_welcome


@app.route('/inspector/users', methods=['POST', 'GET'])
@login_required
def inspector_users_main():
    if not current_user.is_inspector():
        return Response(status=403)
    find_form = FindUserForm()
    no_result = False
    users = None
    show_result = False
    if find_form.validate_on_submit() and request.method == 'POST':
        find_name = find_form.name.data
        find_result = User.query.filter(User.name.ilike('%{}%'.format(find_name))).all()
        no_result = False
        if not find_result:
            no_result = True
        users = list()
        for i in find_result:
            if i.is_inspector() or i.is_admin():
                continue
            current = dict(id=i.id, name=i.name)
            users.append(current)
        show_result = True
    return render_template('jasny/inspector/show_user.html',
                           no_result = no_result,
                           form=find_form,
                           show_result = show_result,
                           data = users,
                           page_name='Пользователи',
                           username=current_user.min_name())


@app.route('/inspector/users/add', methods=['POST', 'GET'])
@login_required
def inspector_users_add():
    if not current_user.is_inspector():
        return Response(status=403)
    add_form = AddUserForm()
    user_for_card = None
    if add_form.validate_on_submit():
        check_words = sum([i.strip(string.punctuation).isalpha() for i in add_form.user_name.data.split()])
        if check_words < 3:
            flash('ФИО пользователя должно содержать минимум 3 слова')
        else:
            username_string = '{}_{}'.format(add_form.user_name.data.split(' ')[0], randint(100,999))
            username = translit(username_string,
                                language_code='ru',
                                reversed=True)
            new_user = User(name = add_form.user_name.data,
                            login = username,
                            email = add_form.email.data,
                            created_by=current_user.id)
            # TODO: Добавить номер телефона в модель
            user_password = generate_password(8)
            new_user.set_password(user_password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Пользователь {0} успешно зарегистрирован в системе'.format(add_form.user_name.data))
                user_for_card = new_user
                user_for_card.password_hash = user_password
                try:
                    send_welcome(add_form.user_name.data, username, user_password, add_form.email.data, insp=False)
                    flash('Учетные данные пользователя отправлена на email {}'.format(add_form.email.data))
                except:
                    flash('Ошибка отправки учетных данных пользователя на email!')
            except Exception as e:
                db.session.rollback()
                flash('Ошибка создания пользователя<br>Техническая информация:<br>{}'.format(e))
    return render_template('jasny/inspector/add_user.html', page_name='Регистрация пользователя',
                           username=current_user.min_name(),
                           user = user_for_card,
                           form=add_form)


@app.route('/inspector/users/show/<int:id>', methods=['POST', 'GET'])
@login_required
def inspector_users_showinfo(id):
    if not current_user.is_inspector():
        return Response(status=403)
    change_form = ChangeUserEmailAndPassword()
    new_data = dict()
    if request.method == 'POST' and change_form.is_submitted():
        updating_data = dict()
        if change_form.email.data:
            updating_data['email'] = change_form.email.data
            new_data['email'] = change_form.email.data
        if change_form.password.data:
            from werkzeug.security import generate_password_hash
            updating_data['password_hash'] = generate_password_hash(change_form.password.data)
            new_data['pass'] = change_form.password.data
        if updating_data:
            User.query.filter_by(id=id).update(updating_data)
            db.session.commit()
            flash('Данные пользователя изменены!')
    user = db.session.query(User.id,
                            User.login,
                           User.name,
                           User.email,
                           User.created_on,
                           User.created_by).filter(User.id == id).first()
    who_registered = ''
    try:
        who_registered = db.session.query(User.name).filter(User.id == user.created_by).first().name
    except:
        who_registered = 'Неизвестно'
    user_flats = Address.query.filter_by(owner=user.id).all()
    return render_template('jasny/inspector/show_user_information.html',
                           user = user,
                           who_registered = who_registered,
                           show_data = True,
                           form=change_form,
                           page_name='Информация о жильце',
                           username=current_user.min_name(),
                           update = new_data,
                           flats=user_flats)


@app.route('/inspector/users/usercard',methods=['POST'])
@login_required
def inspector_usercard():
    if not current_user.is_inspector():
        return Response(status=403)
    if request.method == 'POST' and request.form.get('password') is not None and request.form.get('id') is not None:
        user = db.session.query(User.id, User.name, User.login, User.email).filter_by(id = request.form.get('id')).limit(1).first()
        if not user:
            return Response(status=404)

        return render_template('/jasny/inspector/user_card.html',
                               user=user,
                               page_name='Карточка пользователя',
                               user_password = request.form.get('password'))