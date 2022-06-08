# -*- coding: utf-8 -*-
from app import app, db # Точка входа в приложение Flask
from flask import render_template, redirect, url_for, request, Response
from flask_login import login_required, current_user
from models import Address, House, Counter, Pokaz
from forms import SelectFlatForStats, SelectMeterForStats
from utils import month_name


@app.route('/app/stats', methods=['GET', 'POST'])
@login_required
def stats_main_page():
    if current_user.is_admin():
        return redirect(url_for('admin_page'))
    if current_user.is_inspector():
        return redirect(url_for('inspector_index'))

    user_flats = db.session.query(Address.id, Address.kv, Address.house).filter_by(owner=current_user.id).all()
    search_form = SelectFlatForStats()
    flats_list = list()
    for f in user_flats:
        house_adr = db.session.query(House.adres).filter_by(id=f.house).limit(1).first()
        flats_list.append((f.id, '{} кв. {}'.format(house_adr.adres, f.kv)))
    search_form.flats.choices = flats_list

    if request.method == 'POST' and search_form.validate_on_submit():
        selected_flat = search_form.flats.data
        flat_counters = db.session.query(Counter.id, Counter.name).filter_by(flat=selected_flat).all()
        search_meters_form = SelectMeterForStats()
        search_meters_form.meters.choices = [(m.id, m.name) for m in flat_counters]
        return render_template('/jasny/user/statistics.html',
                               form=search_form,
                               meters_form=search_meters_form,
                               page_name='Статистика',
                               username=current_user.min_name())

    if request.method == 'GET' and request.args.get('meter_id'):
        meter_id=request.args.get('meter_id')
        counter_name = db.session.query(Counter.name, Counter.flat).filter_by(id=meter_id).limit(1).first().name
        flat_info = db.session.query(Address.owner).filter_by(id=counter_name.flat).limit(1).first()
        if flat_info.owner is not current_user.id:
            return Response(status=403)
        counter_pokaz_data = db.session.query(Pokaz.amount,
                                              Pokaz.p_year,
                                              Pokaz.p_month).filter_by(counter=meter_id).all()
        pokaz_periods_names = list()
        pokaz_full_data = list()
        for pkz in counter_pokaz_data:
            if not pkz.p_month or not pkz.p_year:
                continue
            pokaz_periods_names.append('{} {}'.format(month_name(int(pkz.p_month)), pkz.p_year))
            pokaz_full_data.append(pkz.amount)
        # Средние показатели
        if len(pokaz_full_data) > 1:
            i = 0
            average_pkz = list()
            average_periods = list()
            while i < len(pokaz_full_data)-1:
                average = (pokaz_full_data[i] + pokaz_full_data[i+1])/2
                average_period = '{} - {}'.format(pokaz_periods_names[i],pokaz_periods_names[i+1])
                average_pkz.append(average)
                average_periods.append(average_period)
                i = i+1
            return render_template('/jasny/user/statistics.html',
                                   form=search_form,
                                   show_chart=True,
                                   meter_name=counter_name,
                                   periods=pokaz_periods_names,
                                   pokaz=pokaz_full_data,
                                   avg_periods=average_periods,
                                   avg_pokaz=average_pkz,
                                   page_name='Статистика',
                                   username=current_user.min_name())
        return render_template('/jasny/user/statistics.html',
                               form=search_form,
                               show_chart=True,
                               meter_name = counter_name,
                               periods=pokaz_periods_names,
                               pokaz=pokaz_full_data,
                               page_name='Статистика',
                               username=current_user.min_name())

    return render_template('/jasny/user/statistics.html',
                           form=search_form,
                           page_name='Статистика',
                           username=current_user.min_name())