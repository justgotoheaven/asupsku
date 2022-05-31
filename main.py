# -*- coding: utf-8 -*-
from app import app # Точка входа в приложение Flask
import api # API для ajax
from account import auth, account # Аутентификация
from application import app_index, statistics, appeals # Рендеры главной страницы
from admin_section import admin, com_categories, staff# Раздел администратора
from inspector import index, houses, flats, meters, users, appeals, costs

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)