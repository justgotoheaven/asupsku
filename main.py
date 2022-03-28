# -*- coding: utf-8 -*-
from app import app # Точка входа в приложение Flask
import api # API для ajax
import auth # Аутентификация
import views # Рендеры главной страницы
import admin # Раздел администратора

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)