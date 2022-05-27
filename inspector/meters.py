from app import app, db
from flask import Response, render_template, request, flash, send_file
from flask_login import current_user, login_required
from models import Categories, House, Address, Counter, User
from forms import AddMeterForm, ApproveMeterForm, ShowFlatsFilterHouseForm, SelectPeriodForm
from inspector.data_unload import DataUploader
from urllib.parse import quote

@app.route('/inspector/meters/add',methods=['GET', 'POST'])
@login_required
def inspector_meters_add():
    if not current_user.is_inspector():
        return Response(status=403)
    no_flat = False
    if request.args.get('flat_id') is None:
        no_flat = True
    else:
        flat_id = request.args.get('flat_id')
        flat_house = db.session.query(Address.house, Address.kv).filter_by(id=flat_id).limit(1).first()
        address_to_reg = db.session.query(House.adres).filter_by(id=flat_house.house).limit(1).first()
        add_form = AddMeterForm()
        add_form.flat_id.data = flat_id
        add_form.approve_date.data = None
        categories = db.session.query(Categories.id, Categories.name).all()
        add_form.category.choices = [(c.id, c.name) for c in categories]
        if request.method == 'POST' and add_form.is_submitted():
            approved_state = False
            if len(add_form.approve_date.raw_data[0]) > 0:
                approved_state = True
            new_meter = Counter(name=add_form.name.data,
                                category=add_form.category.data,
                                flat=int(flat_id),
                                setup_date=add_form.setup_date.data,
                                setup_on=add_form.setup_on.data,
                                approved=approved_state,
                                approve_date=add_form.approve_date.raw_data[0],
                                next_approve_date=add_form.next_approve_date.data,
                                approve_document=add_form.approve_doc.data,
                                serial_num=add_form.serial_num.data)
            try:
                db.session.add(new_meter)
                db.session.commit()
                flash('Счетчик {} успешно зарегистрирован по адресу {} кв. {}'.format(add_form.name.data,
                                                                               address_to_reg.adres,flat_house.kv))
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при регистрации счетчика! Техническая информация: {}'.format(e))
    return render_template('jasny/inspector/add_meter.html',
                           username=current_user.min_name(),
                           page_name='Регистрация прибора учета',
                           no_flat = no_flat,
                           flat_address = '{}, кв. {}'.format(address_to_reg.adres, flat_house.kv),
                           form=add_form)

@app.route('/inspector/meters')
@login_required
def inspector_meters_mainpage():
    if not current_user.is_inspector():
        return Response(status=403)
    not_approved_meters = db.session.query(Counter.id).filter_by(approved=False).all()
    not_ap_len = 0
    if not_approved_meters:
        not_ap_len = len(not_approved_meters)
    return render_template('/jasny/inspector/show_meters_an.html',
                           page_name='Приборы учета',
                           username=current_user.min_name(),
                           not_approved_amount = not_ap_len)

@app.route('/inspector/meters/not_approved')
@login_required
def inspector_meters_not_approved():
    if not current_user.is_inspector():
        return Response(status=403)
    na_meters = db.session.query(Counter.id,
                                 Counter.flat,
                                 Counter.name,
                                 Counter.setup_on,
                                 Counter.serial_num).filter_by(approved=False).all()
    address = dict()
    for m in na_meters:
        m_flat = db.session.query(Address.house, Address.kv).filter_by(id=m.flat).limit(1).first()
        house_adr = db.session.query(House.adres).filter_by(id=m_flat.house).limit(1).first()
        address[m.id] = '{} кв. {}'.format(house_adr.adres, m_flat.kv)
    return render_template('jasny/inspector/not_ap_meters.html',
                           page_name='Неповеренные ПУ',
                           username=current_user.min_name(),
                           counters=na_meters,
                           address=address)


@app.route('/inspector/meters/approve/<int:id>', methods=['GET','POST'])
@login_required
def inspector_meters_approve(id):
    if not current_user.is_inspector():
        return Response(status=403)
    approve_form = ApproveMeterForm()
    c_info = db.session.query(Counter.name,
                              Counter.setup_on,
                              Counter.flat,
                              Counter.setup_date,
                              Counter.serial_num).filter_by(id=id).limit(1).first()
    m_flat = db.session.query(Address.house, Address.kv).filter_by(id=c_info.flat).limit(1).first()
    house_adr = db.session.query(House.adres).filter_by(id=m_flat.house).limit(1).first()
    address = '{} кв. {}'.format(house_adr.adres, m_flat.kv)
    if request.method == 'POST' and approve_form.validate_on_submit():
        approve_update_data = dict(approved=True,
                                   approve_date=approve_form.approve_date.data,
                                   next_approve_date=approve_form.next_approve_date.data,
                                   approve_document=approve_form.approve_doc.data)
        try:
            Counter.query.filter_by(id=id).update(approve_update_data)
            db.session.commit()
            flash('Прибор учета {} по адресу {} поверен!'.format(c_info.name, address),
                  'alert alert-success')
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при поверке прибора учета {}. '
                  'Техническая информация'.format(c_info.name, e),
                  'alert alert-danger')
    return render_template('jasny/inspector/meter_approve.html',
                           page_name='Поверка ПУ',
                           username=current_user.min_name(),
                           address=address,
                           counter=c_info,
                           form=approve_form)

@app.route('/inspector/meters/unload', methods=['GET','POST'])
@login_required
def inspector_meters_unload_pkz():
    if not current_user.is_inspector():
        return Response(status=403)
    if request.args.get('type') is None:
        return Response(status=400)
    type = int(request.args.get('type'))
    if type == 2:
        filter_form = ShowFlatsFilterHouseForm()
        all_houses = db.session.query(House.id, House.adres).all()
        filter_form.house.choices = [(h.id, h.adres) for h in all_houses]
        show_list = False
        flats = None
        if filter_form.validate_on_submit():
            house_filter = filter_form.house.data
            show_list = True
            flats = Address.query.filter_by(house=house_filter).all()
        return render_template('jasny/inspector/pokaz_unloading_flat.html',
                               username=current_user.min_name(),
                               page_name='Выгрузка показаний',
                               form=filter_form,
                               show_list=show_list,
                               flats=flats)
    elif type == 1:
        filter_form = ShowFlatsFilterHouseForm()
        all_houses = db.session.query(House.id, House.adres).all()
        filter_form.house.choices = [(h.id, h.adres) for h in all_houses]
        return render_template('jasny/inspector/pokaz_unloading_mkd.html',
                               username=current_user.min_name(),
                               page_name='Выгрузка показаний',
                               form=filter_form)
    else:
        return Response(status=400)


@app.route('/inspector/meters/unload_kv', methods=['GET','POST'])
@login_required
def inspector_meters_unload_pkz_kv():
    if not current_user.is_inspector():
        return Response(status=403)
    if request.args.get('kv') is None:
        return Response(status=400)
    flat_id = int(request.args.get('kv'))
    flat = Address.query.filter_by(id=flat_id).limit(1).first()
    period_form = SelectPeriodForm()
    if request.method == 'POST' and period_form.validate_on_submit():
        unloader = DataUploader(type=2,
                                kvid=flat_id,
                                period_start=dict(m=period_form.min_month.data, y=period_form.min_year.data),
                                period_end=dict(m=period_form.max_month.data, y=period_form.max_year.data),
                                user_id=current_user.id)
        link_virtual = unloader.unload_and_push()
        filename = unloader.get_filename()
        return Response(
            link_virtual,
            headers={
                'charset': 'utf-8',
                'Content-Disposition': 'attachment; filename=''{utf_filename}'.format(
                    utf_filename=quote(filename.encode('utf-8'))),
                'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
    return render_template('jasny/inspector/pokaz_unloading_flat_2step.html',
                           username=current_user.min_name(),
                           page_name='Выгрузка показаний',
                           flat=flat,
                           form=period_form)


@app.route('/inspector/meters/unload_mkd', methods=['GET','POST'])
@login_required
def inspector_meters_unload_pkz_mkd():
    if not current_user.is_inspector():
        return Response(status=403)
    if request.args.get('house') is None:
        return Response(status=400)
    house_id = int(request.args.get('house'))
    house_adr = db.session.query(House.adres).filter_by(id=house_id).limit(1).first()
    period_form = SelectPeriodForm()
    if request.method == 'POST' and period_form.validate_on_submit():
        unloader = DataUploader(type=1,
                                mkdid=house_id,
                                period_start=dict(m=period_form.min_month.data, y=period_form.min_year.data),
                                period_end=dict(m=period_form.max_month.data, y=period_form.max_year.data),
                                user_id=current_user.id)
        link_virtual = unloader.unload_and_push()
        filename = unloader.get_filename()
        return Response(
            link_virtual,
            headers={
                'charset': 'utf-8',
                'Content-Disposition': 'attachment; filename=''{utf_filename}'.format(
                    utf_filename=quote(filename.encode('utf-8'))),
                'Content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            })
    return render_template('jasny/inspector/pokaz_unloading_mkd_2step.html',
                           username=current_user.min_name(),
                           page_name='Выгрузка показаний',
                           adr=house_adr.adres,
                           form=period_form)