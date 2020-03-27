from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

#两个装饰器，与index()功能相关联
@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author':{'username':'John'},
            'body':'Beautiful day in Shanghai!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers is cool!'
        }
    ]
    return render_template('index.html',title='Home',user=user,posts=posts)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    #判断GET or POST，用以判别是否需要验证
    if form.validate_on_submit():
        #用以回复用户动作成功与否
        flash('Login requested for user: {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        #重新回到某页面
        return redirect(url_for('index'))
    return render_template('login.html',title='Sign In', form=form)