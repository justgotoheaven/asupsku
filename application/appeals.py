from app import app, db # Точка входа в приложение Flask
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Appeal, User
from forms import AppealsCreate


@app.route('/app/appeals')
@login_required
def appeals_main_page():
    if current_user.is_admin():
        return redirect(url_for('admin_page'))
    if current_user.is_inspector():
        return redirect(url_for('inspector_index'))

    user_appeals = db.session.query(Appeal.id,Appeal.created_on,Appeal.subject,
                                    Appeal.answered).filter_by(created_by=current_user.id).order_by(Appeal.created_on.desc()).all()
    return render_template('jasny/user/appeals_index.html',
                           appeals=user_appeals,
                           page_name='Обращения',
                           username=current_user.min_name())


@app.route('/app/appeals/new',methods=['GET','POST'])
@login_required
def appeals_create_page():
    if current_user.is_admin():
        return redirect(url_for('admin_page'))
    if current_user.is_inspector():
        return redirect(url_for('inspector_index'))

    add_form = AppealsCreate()
    if request.method == 'POST' and add_form.validate_on_submit():
        new_appeal = Appeal(category=1,
                            created_by=current_user.id,
                            subject=add_form.subject.data,
                            text=add_form.text.data)
        try:
            db.session.add(new_appeal)
            db.session.commit()
            flash('Обращение по теме "{}" зарегистрировано в системе. Ожидайте ответа от УК!'.format(add_form.subject.data),'alert alert-success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка подачи обращения. Техническая информация: {}'.format(e),'alert alert-danger')
    return render_template('jasny/user/appeals_create.html',
                           form = add_form,
                           page_name='Обращения',
                           username=current_user.min_name())


@app.route('/app/appeals/<int:id>', methods=['POST', 'GET'])
@login_required
def appeals_info_page(id):
    if current_user.is_admin():
        return redirect(url_for('admin_page'))
    if current_user.is_inspector():
        return redirect(url_for('inspector_index'))

    appeal = Appeal.query.filter_by(id=id).limit(1).first()
    author = db.session.query(User.name).filter_by(id=appeal.created_by).limit(1).first().name
    appeal_answered_by_name = None
    if appeal.answered:
        appeal_answered_by_name = db.session.query(User.name).filter_by(id=appeal.answered_by).limit(1).first().name
    return render_template('jasny/user/appeals_info.html',
                           pagename='Обращение',
                           username=current_user.min_name(),
                           a_aname=appeal_answered_by_name,
                           a=appeal,
                           author=author)