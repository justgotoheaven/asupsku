# -*- coding: utf-8 -*-
from flask_login import UserMixin
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    login = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(300), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)
    email = db.Column(db.String(100), unique=True)
    tgid = db.Column(db.Integer())
    isadmin = db.Column(db.Boolean(), default=False)
    inspector = db.Column(db.Boolean(), default=False)
    created_by = db.Column(db.Integer(), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def min_name(self):
        name = self.name
        if len(name) == 0:
            return 'Пользователь'
        splitted_name = name.split()
        minimize = '{0} {1}.{2}.'.format(splitted_name[0], splitted_name[1][0], splitted_name[2][0])
        return minimize

    def is_admin(self):
        return self.isadmin

    def is_inspector(self):
        return self.inspector

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.login)


class House(db.Model):
    __tablename__ = 'houses'
    id = db.Column(db.Integer(), primary_key=True)
    adres = db.Column(db.String(255), unique=True)
    added_by = db.Column(db.Integer())
    added_on = db.Column(db.DateTime(), default=datetime.now)


class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer(), primary_key=True)
    house = db.Column(db.Integer())
    kv = db.Column(db.Integer(), unique=True)
    owner = db.Column(db.Integer())
    registered_in = db.Column(db.Integer()) # Число зарегистрированных в квартире
    added_by = db.Column(db.Integer())
    added_on = db.Column(db.DateTime(), default=datetime.now)
    changed_on = db.Column(db.Integer())
    changed_by = db.Column(db.DateTime())

    owner_name = None

    def change(self, user):
        self.changed_by = user
        self.changed_on = datetime.now



class Counter(db.Model):
    __tablename__ = 'counter'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Integer(), nullable=False)
    setup_date = db.Column(db.Date())
    setup_on = db.Column(db.String(100))
    approved = db.Column(db.Boolean())
    approve_date = db.Column(db.Date())
    next_approve_date = db.Column(db.Date())
    serial_num = db.Column(db.String(100))
    flat = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)


class Pokaz(db.Model):
    __tablename__ = 'pokaz'
    id = db.Column(db.Integer(), primary_key=True)
    counter = db.Column(db.Integer(), nullable=False)
    pokaz = db.Column(db.Float())
    date = db.Column(db.Date())
    month = db.Column(db.Integer())
    year = db.Column(db.Integer())
    person = db.Column(db.Integer())
    type = db.Column(db.Integer())

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.pokaz)


class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), unique=True)
    description = db.Column(db.String(300))
    added_by = db.Column(db.Integer(), nullable=False)
    added_on = db.Column(db.DateTime(), default=datetime.now)
    cost = db.Column(db.Float())
    cost_changed_on = db.Column(db.DateTime())
    cost_changed_by = db.Column(db.Integer())