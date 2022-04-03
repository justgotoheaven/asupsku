from app import app,db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import User, House
from forms import AddHouseForm


# Добавить МКД в систему
@app.route('/inspector/houses/add', methods=['GET', 'POST'])
@login_required
def inspector_houses_add():
    if not current_user.is_inspector():
        return Response(status=403)
    template_name = 'jasny/inspector/add_house.html'
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
                          added_by = current_user.id)
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