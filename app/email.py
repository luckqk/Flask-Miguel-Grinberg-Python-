from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread

#异步发送邮件
def send_async_email(app, msg):
    #定制线程需要上下文管理，调用app.config中的内容
    with app.app_context():
        mail.send(msg)

def send_eamil(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_eamil('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token),
               )