from flask_mail import Mail, Message
from flask import render_template
from app import app

app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'asupsku@jhvn.tk'
app.config['MAIL_DEFAULT_SENDER'] = 'asupsku@jhvn.tk'
app.config['MAIL_PASSWORD'] = '---'

mail = Mail(app)


def send_welcome(name, login, password, email, insp=False):
    msg = Message("АСУПСКУ: Регистрация", recipients=[email])
    if insp:
        msg.html = render_template('/jasny/email_insp_welcome.html',
                                   login=login,
                                   password=password,
                                   name=name)
    else:
        msg.html = render_template('/jasny/user_card.html',
                                   user_name=name,
                                   user_login=login,
                                   user_password=password)
    mail.send(msg)
