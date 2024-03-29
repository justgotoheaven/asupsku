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
    kv = db.Column(db.Integer())
    owner = db.Column(db.Integer())
    registered_in = db.Column(db.Integer()) # Число зарегистрированных в квартире
    added_by = db.Column(db.Integer())
    added_on = db.Column(db.DateTime(), default=datetime.now)
    changed_on = db.Column(db.DateTime())
    changed_by = db.Column(db.Integer())

    owner_name = None

    def change(self, user):
        self.changed_by = user
        self.changed_on = datetime.now

    def get_full_address(self):
        house = db.session.query(House.adres).filter_by(id=self.house).limit(1).first()
        if not house:
            return False
        adr = '{} кв. {}'.format(house.adres, self.kv)
        return adr

    def get_owner_name(self):
        owner = db.session.query(User.name).filter_by(id=self.owner).limit(1).first()
        if not owner:
            return 'Неизвестно'
        else:
            return owner.name



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
    approve_document = db.Column(db.String(256))
    archived = db.Column(db.Boolean(), default=False)
    archived_by = db.Column(db.Integer())
    archived_on = db.Column(db.DateTime())

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)


class Pokaz(db.Model):
    __tablename__ = 'pokaz'
    id = db.Column(db.Integer(), primary_key=True)
    counter = db.Column(db.Integer(), nullable=False)
    added_by = db.Column(db.Integer())
    added_on = db.Column(db.DateTime(), default=datetime.now)
    approved = db.Column(db.Boolean())
    approved_by = db.Column(db.Integer())
    approved_on = db.Column(db.DateTime())
    amount = db.Column(db.Float())
    p_month = db.Column(db.Integer())
    p_year = db.Column(db.Integer())

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

    @classmethod
    def get_changer_name(self):
        cost_ch = self.cost_changed_by
        user = db.session.query(User.name).filter_by(id=cost_ch).limit(1).first()
        if not user:
            return 'Неизвестно'
        else:
            return user.name


class Appeal(db.Model):
    __tablename__ = 'appeals'
    id = db.Column(db.Integer(), primary_key=True)
    category = db.Column(db.Integer(), nullable=False)
    created_by = db.Column(db.Integer(), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)
    subject = db.Column(db.String(256))
    text = db.Column(db.Text())
    answered = db.Column(db.Boolean(), default=False)
    answered_by = db.Column(db.Integer())
    answered_on = db.Column(db.DateTime())
    answer_text = db.Column(db.Text())
    closed = db.Column(db.Boolean())
