from flask_login import login_user, current_user, logout_user
from flask import session, flash, redirect, url_for
#from flask_session import Session
import psutil

from SA import db

from SA.models import User, Tweet, Author


from textblob import TextBlob
import re

def cleantweet(tweet):
    """Cleans a Tweet - removes breaking non-ASCII characters such as emoji"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    emoji_patternII =	re.compile(u'['
    u'\U0001F300-\U0001F64F'
    u'\U0001F680-\U0001F6FF'
    u'\u2600-\u26FF\u2700-\u27BF]+',
    re.UNICODE)

    tweet =emoji_pattern.sub(r'', tweet)
    tweet =emoji_patternII.sub(r'', tweet)

    tweet = re.sub(r'http\S+', '', tweet)
    tweet = re.sub(r'pic.twitter.com\S+', '', tweet)
    tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])(\w:\/\/\S+)", " ", tweet).split())

    return "".join(i for i in tweet if ord(i)<128)


def getsentiment(tweet):
    """Gets the sentiment value of a Tweet after cleaning it"""
    tweet = cleantweet(tweet)
    tweet = TextBlob(tweet)
    return tweet.sentiment




def Build_JSON_User(item):
    data = {}
    data['username'] = item.username
    data['email'] = item.email
    data['avatar'] = item.avatar
    data['verified'] = item.verified
    data['credits'] = item.credits
    data['token'] = item.token
    data['password_hash'] = item.password_hash

    return data


def Build_JSON_Author(result):
    data = {}
    data['id'] = str(result.id)
    data['handle'] = str(result.handle)
    data['screenname'] = result.screenname
    data['bio'] = result.bio
    data['followertot'] = result.followertot
    data['followingtot'] = result.followingtot
    data['mediatot'] = result.mediatot
    data['verified'] = result.verified
    data['private'] = result.private
    data['joindatetime'] = result.joindatetime
    data['avatar'] = result.avatar

    return data

def Build_JSON_Tweet(result):
    data = {}
    data['id'] = str(result.id)
    data['author_id'] = str(result.author_id)
    data['text'] = result.text
    data['link'] = result.link
    data['location'] = result.location
    data['hashtags'] = result.hashtags
    data['mentions'] = result.mentions
    data['urls'] = result.urls
    data['photos'] = result.photos
    data['video'] = result.video
    data['likes'] = result.likes
    data['retweets'] = result.retweets
    data['replies'] = result.replies
    data['updatetime'] = result.updatetime
    data['sentiment_score'] = getsentiment(cleantweet(result.text))
    data['cleaned_text'] = cleantweet(result.text)

    return data


def gettok():
    """
    Gets user token from session data.
    """
    tok = session["utoken"]
    if tok:
        tok = str(''.join(tok[0]))
    return tok


def tokenverif(AuthWall):
    """
    Checks the user token's validity -
    >> if it has been revoked then resets the session utoken.
    >> Handles AuthWall
    """
    utoken = gettok()
    if utoken:
        user = User.query.filter_by(token=utoken).first()
        if not user:
            session["utoken"] = []
            flash("Invalid Token", "danger")
            return redirect(url_for('misc.index'))
    if AuthWall:
        user = User.query.filter_by(token=utoken).first()
        if not user:
            flash("You need to be logged in to perform this action.")
            return False
    return True


def sessiongen(AuthWall):
    """
    Creates a user session if does not already exist
    > calls token verification if not empty
    """
    if session.get("utoken") is None:
        session["utoken"] = []
    else:
        return tokenverif(AuthWall)


def getstats():
    """
    Gets general system statistics - CPU / Memory Load etc.
    """
    CPU = psutil.cpu_percent()
    MEM = psutil.virtual_memory()
    UserTot = User.query.count()
    TweetTot = Tweet.query.count()
    AuthorTot = Author.query.count()
    DataTot = (UserTot * 7) + (AuthorTot * 13) + (TweetTot * 11)

    return CPU, MEM, UserTot, TweetTot, AuthorTot, DataTot
