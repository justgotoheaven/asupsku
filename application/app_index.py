# -*- coding: utf-8 -*-
from app import app, db # Точка входа в приложение Flask
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Address, House, Counter, Pokaz
from forms import SetPokazForm
from application.pokaz_utils import clear_exists_pkz
from utils import cur_year, get_period

# index page
@app.route('/')
def index():
    try:
        if current_user.is_admin():
            return redirect(url_for('admin_page'))
        elif current_user.is_inspector():
            return redirect(url_for('inspector_index'))
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
    if current_user.is_inspector():
        return redirect(url_for('inspector_index'))

    user_flats = db.session.query(Address.id,
                                  Address.kv,
                                  Address.house).filter_by(owner = current_user.id).all()
    flats_data = list()
    meters_pkz = dict()
    for f in user_flats:
        flat_adress = '{} кв. {}'.format(db.session.query(House.adres).filter_by(id=f.house).limit(1).first().adres, f.kv)
        meter_data = db.session.query(Counter.id, Counter.name, Counter.approved).filter_by(flat=f.id).all()
        for c in meter_data:
            c_pkz_data = db.session.query(Pokaz.amount).filter_by(counter=c.id).order_by(Pokaz.id.desc()).limit(1).first()
            if c_pkz_data:
                meters_pkz[c.id] = c_pkz_data.amount
            else:
                meters_pkz[c.id] = 'Нет данных'
        flat = dict(id=f.id, full_address=flat_adress, meters=meter_data)
        flats_data.append(flat)

    return render_template('jasny/user/user_index.html',
                           page_name='Главная',
                           flat_data = flats_data,
                           m_pkz = meters_pkz,
                           username = current_user.min_name())

    
@app.route('/app/meter/<int:id>')
@login_required
def app_user_meters(id):
    if current_user.is_admin():
        return redirect(url_for('admin_page'))
    if current_user.is_inspector():
        return redirect(url_for('inspector_index'))

    meter = Counter.query.filter_by(id=id).limit(1).first()
    meter_pokaz = db.session.query(Pokaz.amount).filter_by(counter=meter.id).order_by(Pokaz.id.desc()).limit(1).first()
    meter_pokaz_data = 'нет данных'
    if meter_pokaz:
        meter_pokaz_data = meter_pokaz.amount
    flat_info = db.session.query(Address.house, Address.kv).filter_by(id=meter.flat).limit(1).first()
    house = db.session.query(House.adres).filter_by(id=flat_info.house).limit(1).first()
    return render_template('/jasny/user/meter_info.html',
                           page_name='Прибор учета',
                           username=current_user.min_name(),
                           meter=meter,
                           pokaz=meter_pokaz_data,
                           full_address = '{} кв. {}'.format(house.adres, flat_info.kv))


@app.route('/app/pokaz/<int:kvid>', methods=['GET','POST'])
@login_required
def app_user_meters_addpokaz(kvid):
    if current_user.is_admin():
        return redirect(url_for('admin_page'))
    if current_user.is_inspector():
        return redirect(url_for('inspector_index'))

    house = db.session.query(Address.house, Address.kv).filter_by(id=kvid).limit(1).first()
    house_adr = db.session.query(House.adres).filter_by(id=house.house).limit(1).first()
    meters = db.session.query(Counter.id, Counter.name, Counter.approved).filter_by(flat=kvid).all()
    meters_form_data = list()
    for m in meters:
        m_info = dict(counter_name=m.name, counter=m.id)
        if m.approved:
            pokaz = db.session.query(Pokaz.amount).filter_by(counter=m.id).order_by(Pokaz.id.desc()).limit(1).first()
            if pokaz is None:
                m_info['pokaz_current'] = 0.0
            else:
                m_info['pokaz_current'] = pokaz.amount
        else:
            continue
        meters_form_data.append(m_info)
    form = SetPokazForm(counters=meters_form_data)
    if request.method == 'POST' and form.is_submitted():
        data = form.counters.data
        for pkz in data:
            if pkz['pokaz'] is None:
                continue
            clear_exists_pkz(pkz['counter'], get_period(), cur_year())
            pkz_to_save = Pokaz(counter=pkz['counter'],
                                amount=pkz['pokaz'],
                                added_by=current_user.id,
                                p_month=get_period(),
                                p_year=cur_year())
            try:
                db.session.add(pkz_to_save)
                db.session.commit()
                flash('Показания счетчика {} успешно переданы!'.format(pkz['counter_name']), 'alert alert-success')
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при передачи показаний счетчика {}. Техническая информация: {}'.format(pkz['counter_name'], e), 'alert alert-danger')
    return render_template('/jasny/user/add_pkz.html',
                           pagename='Передача показаний',
                           username=current_user.min_name(),
                           form=form,
                           full_address='{} кв. {}'.format(house_adr.adres, house.kv))