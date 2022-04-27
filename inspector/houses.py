from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import User, House, Address
from forms import AddHouseForm


# Добавить МКД в систему
@app.route('/inspector/houses/add', methods=['GET', 'POST'])
@login_required
def inspector_houses_add():
    if not current_user.is_inspector():
        return Response(status=403)
    add_house_form = AddHouseForm()
    if request.method == 'POST' and add_house_form.validate_on_submit():
        new_address = add_house_form.address.data
        checked_house = db.session.query(House.id).filter_by(adres=new_address).limit(1).first()
        if checked_house:
            flash('Ошибка: данный МКД уже зарегистрирован в системе')
            return render_template('jasny/inspector/add_house.html',
                                   form=add_house_form,
                                   page_name='Добавить МКД',
                                   username=current_user.min_name())
        new_house = House(adres=new_address,
                          added_by=current_user.id)
        try:
            db.session.add(new_house)
            db.session.commit()
            flash('МКД по адресу: {} зарегистрирован в системе.'.format(new_address))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка создания МКД. Техническая информация: {}'.format(e))
    return render_template('jasny/inspector/add_house.html',
                           form=add_house_form,
                           page_name='Добавить МКД',
                           username=current_user.min_name())


# Просмотр информации о МКД
@app.route('/inspector/houses', methods=['GET', 'POST'])
@login_required
def inspector_houses_all():
    if not current_user.is_inspector():
        return Response(status=403)
    all_houses = db.session.query(House.id, House.adres).all()
    house_info = list()
    for h in all_houses:
        house = dict(id=h.id,
                     address=h.adres)
        kvart = db.session.query(Address.id).filter_by(house=h.id).all()
        if not kvart:
            house['kvart'] = 0
        else:
            house['kvart'] = len(kvart)
        house_info.append(house)

    return render_template('jasny/inspector/all_houses.html',
                           page_name='Просмотр МКД',
                           username=current_user.min_name(),
                           house_info=house_info)


@app.route('/inspector/houses/<int:id>')
@login_required
def inspector_houses_info(id):
    if not current_user.is_inspector():
        return Response(status=403)
    this_house = House.query.filter_by(id=id).limit(1).first()
    if not this_house:
        return render_template('jasny/inspector/house_info.html',
                               page_name='Информация о МКД',
                               username=current_user.min_name(),
                               not_house=True)
    house = dict(id=this_house.id,
                 adres=this_house.adres,
                 added_on=this_house.added_on)
    added_by_user = db.session.query(User.name).filter_by(id=this_house.added_by).first()
    if added_by_user:
        house['added_by'] = added_by_user.name
    else:
        house['added_by'] = 'Неизвестно'
    return render_template('jasny/inspector/house_info.html',
                           page_name='Информация о МКД',
                           username=current_user.min_name(),
                           show_data=True,
                           house=house)