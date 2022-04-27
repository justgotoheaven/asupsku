from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import Categories, House, Address
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
        categories = db.session.query(Categories.id, Categories.name).all()
        add_form.category.choices = [(c.id, c.name) for c in categories]
        if request.method == 'POST' and add_form.validate_on_submit():
            pass
    return render_template('jasny/inspector/add_meter.html',
                           username=current_user.min_name(),
                           page_name='Регистрация прибора учета',
                           no_flat = no_flat,
                           flat_address = '{}, кв. {}'.format(address_to_reg.adres, flat_house.kv),
                           form=add_form)