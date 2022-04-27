from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import House, Address
from forms import AddFlatForm, ShowFlatsFilterHouseForm

@app.route('/inspector/flats/add',methods=['POST','GET'])
@login_required
def inspector_flats_add():
    if not current_user.is_inspector():
        return Response(status=403)
    houses = db.session.query(House.id, House.adres).all()
    add_form = AddFlatForm()
    add_form.house.choices = [(h.id, h.adres) for h in houses]
    if request.method == 'POST' and add_form.validate_on_submit():
        checked_flat = db.session.query(Address.id).filter_by(kv=add_form.number.data,
                                                              house=add_form.house.data).first()
        if checked_flat:
            flash('Квартира с данным номером уже зарегистрирована в этом МКД')
        else:
            new_flat = Address(house=add_form.house.data,
                               kv=add_form.number.data,
                               added_by=current_user.id)
            house_adres = db.session.query(House.adres).filter_by(id=add_form.house.data).first()

            try:
                db.session.add(new_flat)
                db.session.commit()
                flash('Квартира №{} по адресу {} создана!'.format(add_form.number.data, house_adres.adres))
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при создании квартиры. Техническая информация: {}'.format(e))
    return render_template('jasny/inspector/add_flat.html',
                           page_name='Создание квартиры',
                           username=current_user.min_name(),
                           form=add_form)

@app.route('/inspector/flats/show',methods=['POST','GET'])
@login_required
def inspector_flats_show():
    if not current_user.is_inspector():
        return Response(status=403)
    filter_form = ShowFlatsFilterHouseForm()
    all_houses = db.session.query(House.id, House.adres).all()
    filter_form.house.choices = [(h.id, h.adres) for h in all_houses]
    show_list = False
    if request.args.get('house') is not None:
        house_filter = request.args.get('house')
        show_list = True
        flats = db.session.query(Address.id, Address.kv, Address.owner).filter_by(house=house_filter).all()
        if request.args.get('print') is not None and request.args.get('print') == '1':
            return render_template('jasny/inspector/show_flats_print.html',
                                   page_name='Печать информации о квартирах',
                                   house_adres=db.session.query(House.adres).filter_by(id=house_filter).limit(1).first().adres,
                                   flats=flats)
    return render_template('jasny/inspector/show_flats.html',
                           page_name='Просмотр квартир',
                           username=current_user.min_name(),
                           show_list=show_list,
                           house_adres = db.session.query(House.adres).filter_by(id=house_filter).limit(1).first().adres,
                           house_id=house_filter,
                           flats=flats,
                           form=filter_form)