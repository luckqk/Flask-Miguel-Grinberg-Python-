#各个视图渲染
from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User, Post
from flask_login import logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm, EditProfileForm, PostForm
from datetime import datetime

#两个装饰器，与index()功能相关联
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
#保护函数不受未经身份验证的用户访问
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        #重定向的作用在于提醒用户已经提交动态，若不重定向
        #在刷新页面时会产生重复提交的矛盾
        return redirect(url_for('index'))
    #all()会将结果制成列表
    posts = current_user.followed_posts().all()
    #render_template会渲染参数中的部分
    return render_template('index.html',title='Home Page', form=form, posts=posts)

#登录页面渲染
@app.route('/login', methods=['GET','POST'])
def login():
    #假设用户已经登录，但又到了登录界面
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    #判断GET or POST，用以判别是否需要验证
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        #将用户登录状态注册为已登录
        login_user(user, remember=form.remember_me.data)
        #request 客户端随请求发送的所有信息
        next_page = request.args.get('next')
        #or左边表示url不包含next参数，or右边表示url_parse模块来检测netloc属性用以判断URL相对还是绝对
        #应避免next参数在URL绝对路径下指向一个恶意站点
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        #重新回到指定页面
        return redirect(next_page)
    return render_template('login.html',title='Sign In', form=form)

#登出页面渲染
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#注册页面渲染
@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

#个人主页
@app.route('/user/<username>')
@login_required
def user(username):
    #first or 404 返回第一个或者结果集为空时返回None
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)

#视图函数请求前处理
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#个人主页界面
@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

#关注用户渲染
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return  redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

#取关用户渲染
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}!'.format(username))
    return redirect(url_for('user', username=username))

#探索界面渲染
@app.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)
