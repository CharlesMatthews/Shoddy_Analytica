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

def Get_Account_List(source):
    if source =="app":
        dataout = Author.query.limit(5).all()
    else:
        dataout = Author.query.all()

    return dataout


def Get_Top_Three(handle):
    if handle =="*":
        #dataout = Tweet.query.order_by(Tweet.retweets.desc()).limit(3).all()
        dataout = db.session.query(Tweet, Author).join(Author).order_by(Tweet.retweets.desc()).limit(3).all()
    else:
        result = Author.query.filter_by(handle=handle).first()
        #dataout = Tweet.query.filter_by(author_id = result.id).order_by(Tweet.retweets.desc()).limit(3).all()
        dataout = db.session.query(Tweet, Author).filter_by(author_id = result.id).join(Author).order_by(Tweet.retweets.desc()).limit(3).all()
    return dataout




def Get_Random_Three(handle):
    if handle =="*":
        dataout = Tweet.query.order_by(func.random()).limit(3).all()
        dataout = db.session.query(Tweet, Author).join(Author).order_by(func.random()).limit(3).all()
    else:
        result = Author.query.filter_by(handle=handle).first()
        #dataout = Tweet.query.filter_by(author_id=result.id).order_by(func.random()).limit(3).all()
        dataout = db.session.query(Tweet, Author).filter_by(author_id = result.id).join(Author).order_by(func.random()).limit(3).all()

        """
        print(dataout)
        for tweet, author in dataout:
            print(tweet)
            print(author)
            print(author.id)
        """

    return dataout


def Get_Recent_Three(handle):
    if handle =="*":
        dataout = Tweet.query.limit(3).all()
        dataout = db.session.query(Tweet, Author).join(Author).order_by(Tweet.created_at.desc()).limit(3).all()
    else:
        result = Author.query.filter_by(handle=handle).first()
        #dataout = Tweet.query.filter_by(author_id = result.id).order_by(Tweet.created_at.desc()).limit(3).all()
        dataout = db.session.query(Tweet, Author).filter_by(author_id = result.id).join(Author).order_by(Tweet.created_at.desc()).limit(3).all()

    return dataout



@executor.job
def Email_Scraper_Success(GdriveLink, user):
    token = user.generate_token()
    message = Message(subject="SA - Data Scrape", sender='chenrymatthews@gmail.com', recipients=[user.email])
    message.html = render_template('/emails/html/scraped_result.html', username=user.username, GdriveLink=GdriveLink)
    message.body = f'''Good News everyone! You can access the scraped data here {GdriveLink}
    '''
    mail.send(message)
    return


def list_to_string(list):
    string = "; ".join(str(x) for x in list)
    return string


def Scraped_DB_Insert(Tweets):
    for TweetItem in Tweets:
        try:
            datecombo = TweetItem.datestamp + " " + TweetItem.timestamp
            Tweet_DT =datetime.datetime.strptime(datecombo, '%Y-%m-%d %H:%M:%S')
            Tweet_UDT = datetime.datetime.now()
            """
            print(TweetItem)
            print(TweetItem.id)
            print(TweetItem.user_id)
            print(TweetItem.tweet)
            print(TweetItem.link)
            print(TweetItem.location)
            print(list_to_string(TweetItem.hashtags))
            print(list_to_string(TweetItem.mentions))
            print(list_to_string(TweetItem.urls))
            print(TweetItem.video)
            print(TweetItem.likes_count)
            print(TweetItem.retweets_count)
            print(TweetItem.replies_count)
            print(Tweet_DT)
            print(Tweet_UDT)
            """

            TweetInsert = Tweet(id=TweetItem.id,author_id=TweetItem.user_id, text = TweetItem.tweet, link=TweetItem.link,location = TweetItem.location,
                        hashtags =  list_to_string(TweetItem.hashtags),mentions = list_to_string(TweetItem.mentions),urls =  list_to_string(TweetItem.urls),
                        video = TweetItem.video, likes = TweetItem.likes_count, retweets = TweetItem.retweets_count, replies = TweetItem.replies_count,
                        created_at = Tweet_DT, updatetime = Tweet_UDT)
            db.session.add(TweetInsert)

            db.session.commit()

        except IntegrityError:
            db.session.rollback()
        #print("OwO")
        try:
            #print("OOPSIE WOOPSIE FUCKY WUCKY UWU")
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
            #print(":()")
            db.session.rollback()
        #print(Tweets)

    #print(Tweets[0])
    #print(Tweets[0].id)
    return
##
#
@executor.job
def Scrape_Cleanup(USER, FFN, Tweets):
    FILE_PATH = os.path.join(os.getcwd(),"dataout", "tweets.csv")
    #Scraped_DB_Insert.submit()
    Scraped_DB_Insert(Tweets)
    GdriveLink =  PUSHA.DAYTONA(FILE_PATH, FFN)
    Email_Scraper_Success.submit(GdriveLink, USER)

    os.remove(FILE_PATH)
    print("File Removed!")
    return

@executor.job
def Twint_Scrape_Account(SCRAPE_HANDLE, USER):

    TConfig = twint.Config()
    TConfig.Username = SCRAPE_HANDLE
    TConfig.Store_csv = True
    TConfig.Output = "dataout/tweets.csv"
    TConfig.Store_object = True
    asyncio.set_event_loop(asyncio.new_event_loop())

    twint.run.Search(TConfig)
    Tweets = twint.output.tweets_object
    Scrape_Cleanup.submit(USER, SCRAPE_HANDLE, Tweets)
    #Scrape_Cleanup(USER, SCRAPE_HANDLE, Tweets)
    return


@executor.job
def Twint_Scrape_Query(SCRAPE_QUERY, USER):
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
    #Scrape_Cleanup(USER, SCRAPE_QUERY, Tweets)
    return
