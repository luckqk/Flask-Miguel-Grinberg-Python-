from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail

#异步发送邮件
def send_async_email(app, msg):
    #定制线程需要上下文管理，调用app.config中的内容
    with app.app_context():
        mail.send(msg)

def send_eamil(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           #current_app._get_current_object()从代理对象中提取实际的应用实例
           args=(current_app._get_current_object(), msg)).start()