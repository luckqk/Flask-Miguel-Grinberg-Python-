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