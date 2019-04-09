from SA import db, login_mgr
from flask_login import UserMixin
from SA import login_mgr, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serialiser
from flask import current_app

@login_mgr.user_loader
def Get_User_From_ID(user_id):
    return User.query.get(int(user_id))


#Sets out database structure + key objects used in system - User, Author, Post - their datatypes, validation and relationships.


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    username = db.Column(db.String(20),unique=True, nullable=False)
    avatar = db.Column(db.String(20), nullable=False, default="SA3.svg")
    password_hash = db.Column(db.String(128), nullable=False)
    token = db.Column(db.TEXT, unique=True, nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=0)
    verified = db.Column(db.Boolean, nullable=False, default="0")


    def generate_token(self, expires_sec=2000):
        serialiser = Serialiser(current_app.config["SECRET_KEY"], expires_sec)
        return serialiser.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_token(token):
        serialiser = Serialiser(current_app.config["SECRET_KEY"])
        try:
            user_id = serialiser.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(100), nullable=False)
    screenname = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(400))
    followertot = db.Column(db.Integer)
    followingtot = db.Column(db.Integer)
    liketot = db.Column(db.Integer)
    mediatot = db.Column(db.Integer)
    verified = db.Column(db.Boolean)
    private = db.Column(db.Boolean)
    joindatetime = db.Column(db.DateTime)
    avatar = db.Column(db.TEXT)
    background_image  = db.Column(db.TEXT)
    tweets = db.relationship("Tweet", backref='author', lazy=True)
    updatetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Author('{self.id}','{self.handle}', '{self.avatar}')"



class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    text = db.Column(db.String(400), nullable=False)
    link = db.Column(db.String(800), nullable=False)
    location = db.Column(db.String(200))
    hashtags = db.Column(db.String(400))
    mentions = db.Column(db.String(400))
    urls = db.Column(db.String(400))
    photos = db.Column(db.String(400))
    video = db.Column(db.String(400))
    likes = db.Column(db.Integer)
    retweets = db.Column(db.Integer)
    replies = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, nullable=False)
    updatetime = db.Column(db.DateTime, nullable=False)


#Followers table:
    # Many to many relationship for displaying the following
    # / followed users of a particular author.
#class Followers(db.Model):
#    __tablename__ = 'Followers'
#    userid = db.Column(db.Integer, primary_key=True)
#    followerid = db.Column(db.Integer, nullable=False)
