import datetime

from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import House, Address, Counter, User, Categories
from forms import AddFlatForm, ShowFlatsFilterHouseForm, FindUserForm

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
                               added_by=current_user.id,
                               registered_in=add_form.registered_in.data)
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
    owners = dict()
    if request.args.get('house') is not None:
        house_filter = request.args.get('house')
        house_adres = db.session.query(House.adres).filter_by(id=house_filter).limit(1).first().adres
        show_list = True
        flats = db.session.query(Address.id, Address.kv, Address.owner).filter_by(house=house_filter).all()
        for f in flats:
            owner = db.session.query(User.name).filter_by(id = f.owner).limit(1).first()
            if owner is None:
                owners[f.id] = 'Нет владельца'
            else:
                owners[f.id] = owner.name
        if request.args.get('print') is not None and request.args.get('print') == '1':
            return render_template('jasny/inspector/show_flats_print.html',
                                   page_name='Печать информации о квартирах',
                                   house_adres=db.session.query(House.adres).filter_by(id=house_filter).limit(1).first().adres,
                                   owners=owners,
                                   flats=flats)
        return render_template('jasny/inspector/show_flats.html',
                               page_name='Просмотр квартир',
                               username=current_user.min_name(),
                               show_list=show_list,
                               house_adres = house_adres,
                               house_id=house_filter,
                               flats=flats,
                               form=filter_form,
                               owners=owners)
    return render_template('jasny/inspector/show_flats.html',
                           page_name='Просмотр квартир',
                           username=current_user.min_name(),
                           show_list=show_list,
                           form=filter_form)

@app.route('/inspector/flats/show/<int:id>',methods=['POST','GET'])
@login_required
def inspector_flats_show_by_id(id):
    if not current_user.is_inspector():
        return Response(status=403)
    flat_info = db.session.query(Address).filter_by(id=id).limit(1).first()
    if not flat_info:
        return Response(status=404)
    flat_house = db.session.query(House.adres).filter_by(id=flat_info.house).limit(1).first()
    flat_meters = db.session.query(Counter.name, Counter.id).filter_by(flat=id).all()
    flat_create_user = db.session.query(User.name).filter_by(id=flat_info.added_by).limit(1).first()
    if flat_info.owner is not None:
        flat_owner = db.session.query(User.name).filter_by(id=flat_info.owner).limit(1).first().name
    else:
        flat_owner = 'Нет владельца'
    flat_info.added_by = flat_create_user.name
    return render_template('jasny/inspector/show_flat_info.html',
                           username=current_user.min_name(),
                           page_name='Просмотр информации о квартире',
                           flat_address = '{} кв. {}'.format(flat_house.adres, flat_info.kv),
                           flat = flat_info,
                           flat_owner = flat_owner,
                           meters = flat_meters
                           )


@app.route('/inspector/flats/flat_bind',methods=['POST','GET'])
@login_required
def inspector_flats_bind_owner():
    if not current_user.is_inspector():
        return Response(status=403)
    find_form = FindUserForm()
    no_result = False
    users = None
    show_result = False
    flat_id = request.args.get('flat_id')
    flat_address_data = db.session.query(Address.house, Address.kv).filter_by(id=flat_id).limit(1).first()
    house = db.session.query(House.adres).filter_by(id = flat_address_data.house).limit(1).first()
    flat_address = '{} кв. {}'.format(house.adres, flat_address_data.kv)
    if request.method == 'GET' and request.args.get('flat_id') is not None and request.args.get('new_owner') is not None:
        update_data = dict(owner=request.args.get('new_owner'))
        Address.query.filter_by(id = request.args.get('flat_id')).update(update_data)
        try:
            db.session.commit()
            owner = db.session.query(User.name).filter_by(id=request.args.get(('new_owner'))).limit(1).first()
            return render_template('jasny/inspector/flat_bind_success.html',
                                   page_name='Установка владельца',
                                   username=current_user.min_name(),
                                   flat_address=flat_address,
                                   flat_id = flat_id,
                                   owner_name = owner.name)
        except:
            db.session.rollback()
            return Response(status=500)
    if find_form.validate_on_submit() and request.method == 'POST':
        find_name = find_form.name.data
        find_result = User.query.filter(User.name.ilike('%{}%'.format(find_name))).all()
        no_result = False
        if not find_result:
            no_result = True
        users = list()
        for i in find_result:
            if i.is_inspector() or i.is_admin():
                continue
            current = dict(id=i.id, name=i.name)
            users.append(current)
        show_result = True
    return render_template('jasny/inspector/flat_bind_owner.html',
                           no_result = no_result,
                           form=find_form,
                           show_result = show_result,
                           data = users,
                           flat_id=flat_id,
                           flat_address = flat_address,
                           page_name='Пользователи',
                           username=current_user.min_name())