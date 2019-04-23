#!/usr/bin/python3

import secrets
import os
import time
import asyncio
import datetime


from flask import url_for, current_app, render_template
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from  sqlalchemy.sql.expression import func, select


from threading import Thread
import twint


from SA import db, executor, mail
from SA.models import User, Author, Tweet
from SA.api.api_utils import Export_GDrive
from SA.utils import Build_JSON_Tweet, Build_JSON_Author

import SA.DataPush.KingPush as PUSHA

#Imports Imports IMPORTS! Just cant get enough of them as you can see.... God I HATEHATEHATE package management.

def Get_Account_List(source):
    """
    Gets list of all the authors in the database.
    """
    if source =="app":
        dataout = Author.query.limit(5).all()
    else:
        dataout = Author.query.all()

    return dataout


def Get_Top_Three(handle):
    """
    Returns 3 top tweets from a given author
    """
    if handle =="*":
        dataout = db.session.query(Tweet, Author).join(Author).order_by(Tweet.retweets.desc()).limit(3).all()
    else:
        result = Author.query.filter_by(handle=handle).first()
        dataout = db.session.query(Tweet, Author).filter_by(author_id = result.id).join(Author).order_by(Tweet.retweets.desc()).limit(3).all()
    return dataout




def Get_Random_Three(handle):
    """
    Returns 3 random tweets from a given author
    """
    if handle =="*":
        dataout = Tweet.query.order_by(func.random()).limit(3).all()
        dataout = db.session.query(Tweet, Author).join(Author).order_by(func.random()).limit(3).all()
    else:
        result = Author.query.filter_by(handle=handle).first()

        dataout = db.session.query(Tweet, Author).filter_by(author_id = result.id).join(Author).order_by(func.random()).limit(3).all()

    return dataout


def Get_Recent_Three(handle):
    """
    Returns the 3 most recent tweets of a given author
    """
    if handle =="*":
        dataout = Tweet.query.limit(3).all()
        dataout = db.session.query(Tweet, Author).join(Author).order_by(Tweet.created_at.desc()).limit(3).all()
    else:
        result = Author.query.filter_by(handle=handle).first()
        dataout = db.session.query(Tweet, Author).filter_by(author_id = result.id).join(Author).order_by(Tweet.created_at.desc()).limit(3).all()

    return dataout



@executor.job
def Email_Scraper_Success(GdriveLink, user):
    """
    Emails the user who requested data to be scraped with a Gdrive link
    """
    token = user.generate_token()
    message = Message(subject="SA - Data Scrape", sender='chenrymatthews@gmail.com', recipients=[user.email])
    message.html = render_template('/emails/html/scraped_result.html', username=user.username, GdriveLink=GdriveLink)
    message.body = f'''Good News everyone! You can access the scraped data here {GdriveLink}
    '''
    mail.send(message)
    return


def list_to_string(list):
    """
    Converts a list of data to a string separated by a ; and a space
    """
    string = "; ".join(str(x) for x in list)
    return string


def Scraped_DB_Insert(Tweets):
    """
    Handles inserting Tweets + author to database given a Tweet object from TWINT
    """

    for counter, TweetItem in enumerate(Tweets):
        try:
            datecombo = TweetItem.datestamp + " " + TweetItem.timestamp
            Tweet_DT =datetime.datetime.strptime(datecombo, '%Y-%m-%d %H:%M:%S')
            Tweet_UDT = datetime.datetime.now()


            TweetInsert = Tweet(id=TweetItem.id,author_id=TweetItem.user_id, text = TweetItem.tweet, link=TweetItem.link,location = TweetItem.location,
                        hashtags =  list_to_string(TweetItem.hashtags),mentions = list_to_string(TweetItem.mentions),urls =  list_to_string(TweetItem.urls),
                        video = TweetItem.video, likes = TweetItem.likes_count, retweets = TweetItem.retweets_count, replies = TweetItem.replies_count,
                        created_at = Tweet_DT, updatetime = Tweet_UDT)
            db.session.add(TweetInsert)

            db.session.commit()
            print("Inserted Tweet:" + str(counter) + " \n of: " + str(len(Tweets)))


        except IntegrityError:
            #print("OOPSIE WOOPSIE FUCKY WUCKY UWU")
            db.session.rollback()
            
        try:
            #print("OwO")
            Author_ID, Author_Handle, Author_Screename = TweetItem.user_id, TweetItem.username, TweetItem.name
            Author_FerT, Author_FolT, Author_LikeTot, Author_MediaTot = 0, 0, 0, 0
            Author_Bio, Author_Avatar, Author_BGImg  = "SA- Author Data not retrieved yet!", "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png", ""
            Author_Verif, Author_Priv = False, True
            Author_JoinDT, Author_UDT = datetime.datetime.now(), datetime.datetime.now()
            AuthorInsert = Author(id=Author_ID, handle=Author_Handle, screenname=Author_Screename, bio=Author_Bio, followertot=Author_FerT,
                    followingtot=Author_FolT,liketot=Author_LikeTot,  mediatot=Author_MediaTot, verified = Author_Verif, private= Author_Priv,
                    joindatetime =Author_JoinDT, updatetime= Author_UDT, avatar= Author_Avatar, background_image= Author_BGImg)
            db.session.add(AuthorInsert)
            db.session.commit()

        except IntegrityError:
            print(":()")
            db.session.rollback()

    return
##
#
@executor.job
def Scrape_Cleanup(USER, FFN, Tweets):
    """
    Inserts scraped values to database
    Calls export to Google Drive
    Calls email to user with data link
    """
    FILE_PATH = os.path.join(os.getcwd(),"dataout", "tweets.csv")

    Scraped_DB_Insert(Tweets)
    GdriveLink =  PUSHA.DAYTONA(FILE_PATH, FFN)
    Email_Scraper_Success.submit(GdriveLink, USER)

    os.remove(FILE_PATH)
    print("File Removed!")
    return

@executor.job
def Twint_Scrape_Account(SCRAPE_HANDLE, USER):
    """
    Scrapes a specified Twitter account:
        Stores to csv & object then calls cleanup
    """

    TConfig = twint.Config()
    TConfig.Username = SCRAPE_HANDLE
    TConfig.Store_csv = True
    TConfig.Output = "dataout/tweets.csv"
    TConfig.Store_object = True
    asyncio.set_event_loop(asyncio.new_event_loop())

    twint.run.Search(TConfig)
    Tweets = twint.output.tweets_object
    Scrape_Cleanup.submit(USER, SCRAPE_HANDLE, Tweets)

    return


@executor.job
def Twint_Scrape_Query(SCRAPE_QUERY, USER):
    """
    Scrapes a specified Twitter query:
        Stores to csv & object then calls cleanup
    """
    start_time = time.time()

    TConfig = twint.Config()
    TConfig.Search = SCRAPE_QUERY
    TConfig.Store_csv = True
    TConfig.Output = "dataout/tweets.csv"
    TConfig.Store_object = True
    asyncio.set_event_loop(asyncio.new_event_loop())

    twint.run.Search(TConfig)
    Tweets = twint.output.tweets_object
    Scrape_Cleanup.submit(USER, SCRAPE_QUERY, Tweets)

    return
