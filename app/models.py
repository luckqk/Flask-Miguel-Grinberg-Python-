#用户数据模型和关系
from datetime import datetime
from app import db

#用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    #与另一表posts相关联，Post代表关系多的类，backref代表反向调用时属性名称，lazy关系调用的数据库查询方式
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    #__repr__用于调试时打印实例
    def __repr__(self):
        return '<User {}>'.format(self.username)

#动态发布类
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #下面传入了datetime.utcnow函数，该函数可以自行设计
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


    def __repr__(self):
        return '<Post {}>'.format(self.body)