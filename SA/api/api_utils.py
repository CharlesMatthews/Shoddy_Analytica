from SA import db, executor, mail
from SA.models import User, Author, Tweet
from SA.utils import Build_JSON_Tweet, Build_JSON_Author
from flask_mail import Message
from flask import render_template

import json
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





@executor.job
def RNN_Generate_Text():
    """Generates fresh text from the RNN"""
    RNN.nnout()

@executor.job
def Email_Gdrive_Export(GdriveLink, user):
    """Emails user with exported data result"""

    message = Message(subject="SA - Data Export", sender='chenrymatthews@gmail.com', recipients=[user.email])
    message.html = render_template('/emails/html/export_data.html', username=user.username, GdriveLink=GdriveLink)
    message.body = f'''Good News everyone! You can access the scraped data here {GdriveLink}
    '''
    mail.send(message)
    return

@executor.job # This is a FLASK-EXECUTOR decorator (Async function)
def Export_GDrive(author, usertoken):
    """"""
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
    """
    Inserts Author data scraped by TWINT into database for a given author
    """
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
    """Requests Fresh / new author data from Twitter and then calls insert into DB"""
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
    """Checks that a user token is valid"""
    result = User.query.filter_by(token=token).first()
    if result is None:
        return False
    else:
        return True
