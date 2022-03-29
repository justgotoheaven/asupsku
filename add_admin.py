# -*- coding: utf-8 -*-
from app import db
from models import User

def create_admin(login,password,name):
    admin = User(login=login,
                 name=name,
                 isadmin = True,
                 created_by = -1)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

print('Регистрация администратора\n')
print('Введите имя пользователя: ')
username = input()
print('Введите пароль: ')
password = input()
print('Введите ФИО администратора')
fio = input()

create_admin(username, password, fio)