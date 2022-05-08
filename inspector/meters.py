from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import Categories, House, Address, Counter
from forms import AddMeterForm

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