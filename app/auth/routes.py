#各个视图渲染
from flask import render_template, flash, redirect, url_for, request
from flask_babel import _
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from app import db
from app.auth import bp
from app.models import User
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm

#登录页面渲染
@bp.route('/login', methods=['GET','POST'])
def login():
    #假设用户已经登录，但又到了登录界面
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    #判断GET or POST，用以判别是否需要验证
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        #将用户登录状态注册为已登录
        login_user(user, remember=form.remember_me.data)
        #request 客户端随请求发送的所有信息
        next_page = request.args.get('next')
        #or左边表示url不包含next参数，or右边表示url_parse模块来检测netloc属性用以判断URL相对还是绝对
        #应避免next参数在URL绝对路径下指向一个恶意站点
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        #重新回到指定页面
        return redirect(next_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)

#登出页面渲染
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

#注册页面渲染
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)

#重置密码邮箱界面渲染
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                               title=_('Reset Password'), form=form)

#重置密码界面渲染
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)