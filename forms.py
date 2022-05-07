# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, HiddenField, IntegerField, SelectField, \
    DateField, BooleanField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email


# Форма авторизации пользователя (/account/login)
class LoginForm(FlaskForm):
    login = StringField(validators=[DataRequired()], id="login", render_kw={'placeholder': 'Логин'})
    password = PasswordField(validators=[DataRequired()], id="password", render_kw={'placeholder': 'Пароль'})


# Форма регистрации инспектора
class AddInspectorForm(FlaskForm):
    insp_name = StringField(validators=[DataRequired()], id="insp_name")
    insp_email = EmailField(validators=[DataRequired()], id="insp_email")


# Форма регистрации пользователя
class AddUserForm(FlaskForm):
    user_name = StringField(validators=[DataRequired()], id='user_name')
    email = StringField(validators=[DataRequired()], id='user_email')
    tel = StringField(name='user_tel')



class FindInspectorForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(min=3)], id="name",
                       render_kw={'placeholder': 'Введите имя...'})


class FindUserForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(min=3)], id="name",
                       render_kw={'placeholder': 'Введите имя...'})


class ChangeInspectorEmailAndPassword(FlaskForm):
    email = EmailField(id="new_email", render_kw={'placeholder': 'Введите новый E-mail...'})
    password = StringField(validators=[Length(min=8)], render_kw={'placeholder': 'Введите новый пароль...'})


class ChangeUserEmailAndPassword(FlaskForm):
    email = EmailField(id="new_user_email", render_kw={'placeholder': 'Введите новый E-mail...'})
    password = StringField(id="new_user_password", validators=[Length(min=8)], render_kw={'placeholder': 'Введите новый пароль...'})

class DeleteInspector(FlaskForm):
    submit = SubmitField(label='Да, удалить инспектора')


class AddCategoryForm(FlaskForm):
    cat_name = StringField(validators=[DataRequired(), Length(min=3)], id='cat_name',
                           render_kw={'placeholder': 'Введите наименование...'})
    cat_desc = StringField(validators=[DataRequired()], id="cat_desc", render_kw={'placeholder': 'Введите описание...'})


class DeleteCategory(FlaskForm):
    submit = SubmitField(label='Да, удалить категорию')


class AddHouseForm(FlaskForm):
    address = HiddenField(id='address_text', name='address_text', validators=[DataRequired()])
    selected_kladr = HiddenField(id='selected_kladr', validators=[DataRequired()])


class AddFlatForm(FlaskForm):
    number = IntegerField(validators=[DataRequired()], id="flat_number")
    house = SelectField(validators=[DataRequired()], coerce=int, validate_choice=True)
    registered_in = IntegerField(validators=[DataRequired()], id='flat_registered_in')


class AddMeterForm(FlaskForm):
    name = StringField(validators=[DataRequired(), Length(min=3)], name='meter_name')
    category = SelectField(validators=[DataRequired()], coerce=int, validate_choice=True, name='meter_category')
    serial_num = StringField(validators=[DataRequired(), Length(min=6)], name='meter_serial_num')
    setup_on = StringField(validators=[DataRequired(), Length(min=5)], name='meter_setup_on')
    setup_date = DateField(name='meter_setup_date')

    approve_date = DateField(name='meter_approve_date')
    next_approve_date = DateField(name='meter_next_approve_date')
    flat_id = HiddenField(name='meter_flat')


class ShowFlatsFilterHouseForm(FlaskForm):
    house = SelectField(validators=[DataRequired()], name='house')


class SetPokazCountersForm(FlaskForm):
    counter = HiddenField()
    counter_name = HiddenField()
    pokaz = FloatField()


class SetPokazForm(FlaskForm):
    counters = FieldList(FormField(SetPokazCountersForm))