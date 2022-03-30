# -*- coding: utf-8 -*-
from app import app # Точка входа в приложение Flask
from flask import session, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import User, Counter, Pokaz # Модели и база данных
import utils

# index page
@app.route('/')
def index():
    try:
        if current_user.is_admin():
            return redirect(url_for('admin_page'))
        else:
            return redirect(url_for('app_main'))
    except:
        return redirect(url_for('app_main'))

# application index page
@app.route('/app')
@login_required
def app_main():
    if current_user.is_admin():
        return redirect(url_for('admin_page'))    
    counters = Counter.query.filter(Counter.owner == current_user.id).all()
    counters_data = []
    for c in counters:
        pkz = Pokaz.query.filter(Pokaz.counter == c.id).order_by(Pokaz.id.desc()).first()
        if pkz:
            c.pokaz = pkz.pokaz
        else:
            c.pokaz = 0.0
        c_data = [c.id,c.name,c.pokaz]
        counters_data.append(c_data)
    #Информация о месяцах
    month_info = []
    for m in range(1,12+1):
        if(utils.now_month()-m > 1 or utils.now_month()-m < -1):
            continue
        data = {}
        data['num'] = m
        data['name'] = utils.month_name(m)
        if m == utils.now_month():
            data['now'] = 1
        else:
            data['now'] = 0
        month_info.append(data)
        
    return render_template('jasny/user_index.html',
                           page_name='Главная',
                           username = current_user.min_name(),
                           cdata=counters_data,
                           month_data=month_info)
    
    
    
    