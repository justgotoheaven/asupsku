# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length

# Форма авторизации пользователя (/account/login)
class LoginForm(FlaskForm):
    login = StringField(validators=[DataRequired()],id="login",render_kw={'placeholder':'Логин'})
    password = PasswordField(validators=[DataRequired()],id="password",render_kw={'placeholder':'Пароль'})

# Форма регистрации инспектора
class AddInspectorForm(FlaskForm):
    insp_name = StringField(validators=[DataRequired()], id="insp_name")
    insp_email = EmailField(validators=[DataRequired()], id="insp_email")

#Форма регистрации пользователя
class AddUserForm(FlaskForm):
    user_name = StringField(validators=[DataRequired()], id='user_name')
    email = StringField(id='user_email')
    tel = StringField

class FindInspectorForm(FlaskForm):
    name = StringField(validators=[DataRequired(),Length(min=3)],id="name",render_kw={'placeholder':'Введите имя...'})
