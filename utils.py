# -*- coding: utf-8 -*-
import datetime
import random


def month_name(num):
    ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
          'Октябрь', 'Ноябрь', 'Декабрь']
    return ru[num - 1]


def generate_password(len: int):
    pas = ''
    for x in range(len):  # Количество символов (16)
        pas = pas + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))
    return pas


def get_period():
    current_date = datetime.datetime.now()
    month = int(current_date.strftime('%m'))
    return month


def cur_year():
    d = datetime.datetime.now()
    year = int(d.strftime('%Y'))
    return year
