#用户数据模型和关系
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
#头像服务
from hashlib import md5
from time import time
import jwt
from app import app

#用户关联表,辅助表
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#用户表
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    #与另一表posts相关联，Post代表关系多的类，backref代表反向调用时属性名称，lazy关系调用的数据库查询方式
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    #多对多相互关注关系
    #a关注b这种关系叫followed，b的粉丝列表followers包含a
    followed = db.relationship(
        'User', secondary=followers,
        #通过关系表关联到左侧实体的条件,follower
        primaryjoin=(followers.c.follower_id == id),
        #通过关系表关联到右侧实体的条件,followed
        secondaryjoin=(followers.c.followed_id == id),
        #右侧实体访问该关系的方式
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic')

    #__repr__用于调试时打印实例
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    #头像获取
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    #添加关注
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    #取消关注
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    #从self的关注名单中，根据followers这个辅助表找到是否有匹配user的
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    #查询关注用户以及自身的动态更新
    #join 联合查询，创建一个临时表，将Post用户动态表与followers关系表联合
    #     查找符合 == 判断的动态
    #filter对新表进行过滤，留下满足 == 条件的
    #order_by再按照时间进行排序
    def followed_posts(self):
        #关注用户的更新
        followed = Post.query.join(
            followers,(followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        #自身的动态更新
        own = Post.query.filter_by(user_id=self.id)
        #合并排序
        return followed.union(own).order_by(Post.timestamp.desc())

    #产生jwt令牌
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password':self.id, 'exp':time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    #静态方法，验证失败返回None，成功返回用户ID
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

#动态发布类
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #下面传入了datetime.utcnow函数，该函数可以自行设计
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

#此处id为字符串类型转换为int型
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

