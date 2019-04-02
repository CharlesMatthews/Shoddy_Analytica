from SA import db, executor, mail
from SA.models import User, Author, Tweet
from SA.utils import Build_JSON_Tweet, Build_JSON_Author
from flask_mail import Message
from flask import render_template

from textblob import TextBlob
import json
import re
import os
import csv
import os
import time
import asyncio
import datetime

import SA.NeuralNet.sa_rnn as RNN
import SA.DataPush.KingPush as PUSHA

from threading import Thread
import twint


def cleantweet(tweet):
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
    tweet = cleantweet(tweet)
    tweet = TextBlob(tweet)
    return tweet.sentiment


@executor.job
def RNN_Generate_Text():
    RNN.nnout()

@executor.job
def Email_Gdrive_Export(GdriveLink, user):

    message = Message(subject="SA - Data Export", sender='chenrymatthews@gmail.com', recipients=[user.email])
    message.html = render_template('/emails/html/export_data.html', username=user.username, GdriveLink=GdriveLink)
    message.body = f'''Good News everyone! You can access the scraped data here {GdriveLink}
    '''
    mail.send(message)
    return

@executor.job
def Export_GDrive(author, usertoken):
    if author =="*":
        Tweets = Tweets.query.all()

    user = User.query.filter_by(token=usertoken).first()
    token = user.generate_token()

    Tweets = Tweet.query.filter_by(author=author).all()


    FILE_NAME2 = token +".csv"
    FILE_NAME = "tweets.csv"
    print(FILE_NAME)
    FILE_PATH = os.path.join(os.getcwd(), FILE_NAME)
    #FILE_PATH = os.path.join(os.getcwd(),"SA","DataPush", FILE_NAME)
    #FILE_PATH2 = os.path.join(os.getcwd(),"SA","DataPush", FILE_NAME2)
    #BUILD OUT DB REQUEST TO CSV TONIGHT
    """
    c = csv.writer(open(FILE_PATH2, "w"))
    for item in Tweets:
        c.writerow([item.id,item.author_id, item.text, item.link, item.location, item.hashtags, item.mentions, item.likes, item.retweets, item.replies, item.updatetime])
    """


    GdriveLink = PUSHA.DAYTONA(FILE_PATH, author.handle)

    Email_Gdrive_Export.submit(GdriveLink, user)

    return


def InsertAuthorData(author, AuthorData):
#13 Sep 2017 2:12 PM
#%b %d %Y %I:%M%p
    datecombo = AuthorData.join_date + " " + AuthorData.join_time
    Author_DT =datetime.datetime.strptime(datecombo, '%d %b %Y %I:%M %p')
    Author_UDT = datetime.datetime.now()


    print("\n\n")
    print(dir(AuthorData))
    print("\n\n")

    author.private  = AuthorData.is_private
    author.verified  = AuthorData.is_verified
    author.followingtot  = AuthorData.following
    author.followertot  = AuthorData.followers
    author.joindatetime  = Author_DT
    author.updatetime = Author_UDT
    author.avatar  = AuthorData.avatar
    author.mediatot  = AuthorData.media_count
    author.liketot  = AuthorData.likes
    author.bio  = AuthorData.bio
    author.background_image  = AuthorData.background_image
    db.session.commit()


    """
    author.private = AuthorData.private
    author.bio = AuthorData.bio
    author.mediatot = AuthorData.Media
    """


def GetAuthorData(author):
    c = twint.Config()

    c.Username = author.handle
    c.Limit = 1
    c.Store_object = True
    c.User_full = True
    asyncio.set_event_loop(asyncio.new_event_loop())
    twint.run.Lookup(c)
    AuthorData = twint.output.user_object
    InsertAuthorData(author, AuthorData.pop())



def checktoken(token):
    result = User.query.filter_by(token=token).first()
    if result is None:
        return False
    else:
        return True
