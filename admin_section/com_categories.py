import os
import sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from app import app, db
from models import User, Categories
from flask_login import login_required, current_user
from flask import Response, render_template, request, flash
from forms import AddCategoryForm, DeleteCategory
from datetime import datetime


@app.route('/admin/categories', methods=['POST', 'GET'])
@login_required
def admin_categories_index():
    if not current_user.is_admin():
        return Response(status=403)
    template = 'jasny/admin/categories/categories.html'
    add_form = AddCategoryForm()

    if request.method == 'POST' and add_form.validate_on_submit():
        new_cat = Categories(name=add_form.cat_name.data,
                             description=add_form.cat_desc.data,
                             added_by=current_user.id,
                             cost=0,
                             cost_changed_by=current_user.id,
                             cost_changed_on=datetime.now())
        try:
            db.session.add(new_cat)
            db.session.commit()
            flash('Категория {} успешно создана'.format(add_form.cat_name.data))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка создания категории. Техническая информация: {}'.format(e))

    categories_from_db = db.session.query(Categories.id,
                                          Categories.name,
                                          Categories.description).all()
    if not categories_from_db:
        return render_template(template,
                               page_name='Категории услуг',
                               username=current_user.min_name(),
                               empty=True,
                               form=add_form)
    else:
        return render_template(template,
                               page_name='Категории услуг',
                               username=current_user.min_name(),
                               categories=categories_from_db,
                               form=add_form)
    return render_template(template,
                           page_name='Категории услуг',
                           username=current_user.min_name(),
                           form=add_form)


@app.route('/admin/categories/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def admin_delete_category(id):
    if not current_user.is_admin():
        return Response(status=403)
    template = 'jasny/admin/categories/delete_category.html'
    check_category = Categories.query.filter_by(id = id).first()
    if not check_category:
        return render_template(template,
                               page_name='Удаление категории',
                               username=current_user.min_name(),
                               not_found = True)
    cat_data = db.session.query(Categories.name).filter_by(id=id).first()
    delete_form = DeleteCategory()
    if request.method == 'POST' and delete_form.is_submitted():
        to_delete_cat = Categories.query.filter_by(id = id).first()
        db.session.delete(to_delete_cat)
        db.session.commit()
        return render_template('jasny/admin/categories/category_delete_ok.html',
                               username=current_user.min_name(),
                               page_name='Удаление категории',
                               cat_name = cat_data.name)
    return render_template(template,
                           page_name='Удаление инспектора',
                           username=current_user.min_name(),
                           form=delete_form,
                           cat_id = id,
                           cat_name = cat_data.name)


@app.route('/admin/categories/check/<int:id>', methods=['POST', 'GET'])
@login_required
def admin_check_category(id):
    if not current_user.is_admin():
        return Response(status=403)
    template = 'jasny/admin/categories/category_show_info.html'
    category = Categories.query.filter_by(id = id).first()
    if not category:
        return render_template(template,
                               page_name='Просмотр категории',
                               username = current_user.min_name(),
                               not_cat = True)
    who_register = ''
    who_changed_cost = ''
    try:
        who_register = db.session.query(User.name).filter_by(id=category.added_by).first().name
    except:
        who_register = 'Неизвестно'
    try:
        who_changed_cost = db.session.query(User.name).filter_by(id=category.cost_changed_by).first().name
    except:
        who_changed_cost = 'Неизвестно'
    cat_ex = dict(added_by=who_register,
                  cost_changed_by=who_changed_cost)
    return render_template(template,
                           page_name='Просмотр категории',
                           username = current_user.min_name(),
                           show_data=True,
                           cat=category,
                           cat_ex = cat_ex)