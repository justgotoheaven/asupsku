# -*- coding: utf-8 -*-
import datetime
import random


def month_name(num):
    ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
          'Октябрь', 'Ноябрь', 'Декабрь']
    return ru[num - 1]


def now_month():
    return int(datetime.datetime.now().month)


def generate_password(len: int):
    pas = ''
    for x in range(len):  # Количество символов (16)
        pas = pas + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ'))
    return pas