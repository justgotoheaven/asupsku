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
    day = int(current_date.strftime('%d'))
    prev_month = month - 1
    if prev_month == 0:
        prev_month = 12
    if day > 25-1:
        return month
    else:
        return prev_month


def cur_year():
    d = datetime.datetime.now()
    year = int(d.strftime('%Y'))
    if int(d.strftime('%d')) < 25 and int(d.strftime('%m')) == 1:
        return year-1
    return year
