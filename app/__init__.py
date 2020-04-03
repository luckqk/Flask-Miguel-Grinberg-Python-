#app实例的创建及初始化
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request, current_app
from flask_babel import Babel, lazy_gettext as _l
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
#_l延迟评估，直到被使用了才进行评估
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()

#工厂函数创建
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    #注册错误相关blueprint
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    #注册认证相关blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    #注册blog主功能
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            #创建一个SMTPHandler实例
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'],app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            #设置反馈的问题需要错误级别
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        #设置日志记录
        #rotating log 限制了log的大小
        if not os.path.exists('logs'):
            os.mkdir('logs')
        #maxByte 日志大小10 KB， backupCount 最后保留的日志文件个数
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
        #设置log格式
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        #log常用等级划分DEBUG,INFO,WARNING,ERROR,CRITICAL
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

@babel.localeselector
def get_locale():
    #flask request对象，处理客户端发送的带Accept-Language头部的请求
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    #return 'es'

from app import models