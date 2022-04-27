from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import House, Address
from forms import AddFlatForm

@app.route('/inspector/flats/add',methods=['POST','GET'])
@login_required
def inspector_flats_ass():
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