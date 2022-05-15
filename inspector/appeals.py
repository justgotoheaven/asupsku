from app import app, db
from flask import Response, render_template, request, flash
from flask_login import current_user, login_required
from models import Appeal, User
from forms import AppealsAnswer
from datetime import datetime

@app.route('/inspector/appeals',methods=['POST','GET'])
@login_required
def inspector_appeals_mainpage():
    if not current_user.is_inspector():
        return Response(status=403)

    if request.method == 'GET' and request.args.get('archive') is not None:

        ap_archive = Appeal.query.filter_by(answered=True).order_by(Appeal.id.desc()).all()
        appeals_crnames = dict()
        for p in ap_archive:
            created_by_name = db.session.query(User.name).filter_by(id=p.created_by).limit(1).first()
            appeals_crnames[p.id] = created_by_name.name
        return render_template('jasny/inspector/appeals_archive.html',
                               page_name='Архив обращений',
                               username=current_user.min_name(),
                               appeals=ap_archive,
                               a_crnames=appeals_crnames)

    pending_appeals = db.session.query(Appeal.id,
                                       Appeal.created_by,
                                       Appeal.created_on,
                                       Appeal.subject).order_by(Appeal.id.desc()).filter_by(answered=False).all()
    appeals_crnames = dict()
    for p in pending_appeals:
        created_by_name = db.session.query(User.name).filter_by(id=p.created_by).limit(1).first()
        appeals_crnames[p.id] = created_by_name.name

    return render_template('jasny/inspector/appeals_index.html',
                           page_name='Обращения',
                           appeals=pending_appeals,
                           a_crnames=appeals_crnames,
                           username=current_user.min_name())


@app.route('/inspector/appeals/<int:id>',methods=['POST','GET'])
@login_required
def inspector_appeals_info_answer(id):
    if not current_user.is_inspector():
        return Response(status=403)

    answer_form = AppealsAnswer()
    appeal = Appeal.query.filter_by(id=id).limit(1).first()
    author = db.session.query(User.name).filter_by(id=appeal.created_by).limit(1).first().name
    appeal_answered_by_name = None
    if appeal.answered:
        appeal_answered_by_name = db.session.query(User.name).filter_by(id=appeal.answered_by).limit(1).first().name
    if request.method == 'POST' and answer_form.validate_on_submit():
        answer = answer_form.answer.data
        appeal_answered_by_name = current_user.name
        update_data = dict(answered=True,
                           answered_by=current_user.id,
                           answered_on=datetime.now(),
                           answer_text=answer)
        try:
            Appeal.query.filter_by(id=id).update(update_data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Ошибка ответа на обращение. Техническая информация: {}'.format(e),'alert alert-danger')
    return render_template('jasny/inspector/appeals_info.html',
                           pagename='Обращение',
                           username=current_user.min_name(),
                           form=answer_form,
                           a_aname=appeal_answered_by_name,
                           a=appeal,
                           author=author)