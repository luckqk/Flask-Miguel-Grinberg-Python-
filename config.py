#app相关配置
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #判断是否有database_url，若没有就进行配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or\
        'sqlite:///' + os.path.join(basedir, 'app.db')
    #数据变更后是否发送通知给应用
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #email配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    #TLS加密协议
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #接收错误的电子邮箱列表
    ADMINS = ['mvdlkq@sohu.com']

    #定义了每页展示的项数
    POSTS_PER_PAGE = 3