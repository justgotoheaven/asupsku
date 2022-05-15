import datetime

from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import Categories
from forms import ChangeCostForm


@app.route('/inspector/costs', methods=['POST','GET'])
@login_required
def inspector_costs_mainpage():
    if not current_user.is_inspector():
        return Response(status=403)
    categories = db.session.query(Categories.id,
                                  Categories.name,
                                  Categories.description,
                                  Categories.cost).all()
    return render_template('jasny/inspector/costs_main.html',
                           categories=categories,
                           page_name='Тарифы',
                           username=current_user.min_name())


@app.route('/inspector/costs/change/<int:cid>', methods=['POST','GET'])
@login_required
def inspector_costs_change(cid):
    if not current_user.is_inspector():
        return Response(status=403)
    cat_info = Categories.query.filter_by(id=cid).limit(1).first()
    cat_cost = cat_info.cost
    cat_changer = cat_info.get_changer_name()
    cat_name = cat_info.name
    cat_info = dict(cat_cost=cat_cost,
                    cat_changer_name=cat_changer,
                    cat_name=cat_name,
                    cat_changed_on=cat_info.cost_changed_on)
    change_form = ChangeCostForm()
    if request.method == 'POST' and change_form.validate_on_submit():
        if change_form.new_cost.data < 1:
            flash('Введена некорректная сумма!','alert alert-danger')
        else:
            upd_cat_data = dict(cost = change_form.new_cost.data,
                                cost_changed_by = current_user.id,
                                cost_changed_on = datetime.datetime.now())
            try:
                Categories.query.filter_by(id=cid).update(upd_cat_data)
                db.session.commit()
                flash('Тариф категории {} успешно обновлен!'.format(cat_name),'alert alert-success')
            except Exception as e:
                db.session.rollback()
                flash('Ошибка обновления тарифа. Техническая информация: {}'.format(e),'alert alert-danger')
    return render_template('jasny/inspector/costs_change.html',
                           page_name='Изменение тарифа',
                           username=current_user.min_name(),
                           cat_info=cat_info,
                           form=change_form)
