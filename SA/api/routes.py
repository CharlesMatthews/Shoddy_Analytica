from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template
from flask_api import FlaskAPI, status, exceptions
from flask_login import login_user, current_user, logout_user, login_required
from flask_api import status, exceptions

from SA import db, crypt, executor
from SA.models import User, Author, Tweet
import SA.api.api_utils as apiut
import SA.utils as ut

import requests
import json
import os
import datetime
api = Blueprint('api', __name__)

@api.route("/api/<id>/data")
def ApiAuthorData(id):
    """
    Returns Account data for the specified user/ Tweet

    """
    tok = request.args.get('token')
    type = request.args.get('type')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN

    json_data = {}

    if type =="author":
        dataout = Author.query.get(id)
        if dataout is None:
            error = {'Author_Exists': 'False'}
            return error, status.HTTP_400_BAD_REQUEST
        json_data = ut.Build_JSON_Author(dataout)



    elif type=="tweet":
        dataout = Tweet.query.get(id)
        if dataout is None:
            error = {'Tweet_Exists': 'False'}
            return error, status.HTTP_400_BAD_REQUEST
        json_data = ut.Build_JSON_Tweet(dataout)
        json_data['sentiment_score'] = apiut.getsentiment(dataout.text)
    return json_data, status.HTTP_200_OK



@api.route("/api/getsentiment")
def ApiSentiment():
    """Cleans Data and returns Textblob Output for sentiment of a tweet.
    """
    tok = request.args.get('token')
    tweetid = request.args.get('tweetid')



    if tweetid is not None:
        dataout = Tweet.query.get(tweetid)
    else:
        error = {'Tweet_Exists': 'False'}
        return error, status.HTTP_400_BAD_REQUEST

    jsonout = {}
    jsonout['sentiment_score'] = apiut.getsentiment(dataout.text)


    return jsonout, status.HTTP_200_OK





@api.route("/api/<author>/toptweet")
def ApiAuthortTop(author, methods=['POST', 'GET']):
    """Returns the top tweet of the specified user"""

    end = request.args.get('end')
    tok = request.args.get('token')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN

    if author == "*":
        dataout = Tweet.query.order_by(Tweet.retweets.desc()).limit(end).all()
    else:
        result = Author.query.filter_by(handle=author).first()
        if result is None:
            error = {'Author_Exists': 'False'}
            return error, status.HTTP_400_BAD_REQUEST
        dataout = Tweet.query.filter_by(Tweet.handle == author).order_by(Tweet.retweets.desc()).limit(end).all()

    jsonlist =[]
    for item in dataout:
        json_data = ut.Build_JSON_Tweet(item)
        jsonlist.append(json_data)

    return jsonlist, status.HTTP_200_OK

@api.route("/api/<author>/tweets")
def ApiAuthorTweets(author, methods=['POST', 'GET']):
    """Returns Tweet archive of specified user
        Example Request:

        Example Response:

    """
    tok = request.args.get('token')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN

    offset = request.args.get('offset')
    end = request.args.get('end')
    random = request.args.get('random')

    if author == "*":
        if random == True:
            dataout =Tweet.query.order_by(random()).offset(offset).limit(end).all()
        else:
            dataout =Tweet.query.offset(offset).limit(end).all()
    else:
        aid = Author.query.filter_by(handle=author).first()
        aid = aid.id
        if random == True:
            dataout =Tweet.query.filter_by(author_id = aid).order_by(random()).offset(offset).limit(end).all()
        else:
            dataout = Tweet.query.filter_by(author_id = aid).offset(offset).limit(end).all()

    jsonlist =[]
    for item in dataout:
        json_data = ut.Build_JSON_Tweet(item)
        json_data['sentiment_score'] = apiut.getsentiment(item.text)
        jsonlist.append(json_data)

    return jsonlist, status.HTTP_200_OK



@api.route("/api/<author>/export")
def ApiAuthorExport(author, methods=['POST', 'GET']):
    """Returns Tweet archive of specified user
        Example Request:

        Example Response:

    """
    tok = request.args.get('token')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN


    if author != "*":
        author = Author.query.filter_by(handle=author).first()

        if author is None:
            error = {'Author Exists': 'False'}
            return error, status.HTTP_400_BAD_REQUEST

    apiut.Export_GDrive.submit(author, tok)
    flash("Thanks - Expect an email from us shortly with links! 👀", 'info')
    return redirect(url_for('misc.index'))


@api.route("/api/neuralnet", methods=['POST', 'GET'])
def ApiRNN():
    """

    Gets the last output of the RNN in the generated output textfile.

    Also Calls NeuralNet to genereate a new output and store to text file IF POST REQUEST MADE to reduce load on the NN.

    """
    tok = request.args.get('token')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN

    filepath = os.path.join(os.getcwd(),"SA","NeuralNet", "generated_output.txt")
    print(filepath)

    file = open(filepath, "r")

    message = file.read()

    if request.method == 'POST':
        apiut.RNN_Generate_Text.submit()
        flash("Got your request! Expect the NN output to be updated soon.", 'success')

        Forward = request.args.get("next")
        if Forward:
            return redirect(Forward)
        else:
            return redirect(url_for('misc.index'))

    return render_template("webapp/nnout.html", message =message)


@api.route("/api/authors", methods=['POST', 'GET'])
def ApiAuthorList():
    """Returns list of available accounts along with associated account data.
    """
    tok = request.args.get('token')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN

    dataout = Author.query.all()

    jsonlist =[]
    for item in dataout:
        json_data = ut.Build_JSON_Author(item)
        jsonlist.append(json_data)

    return jsonlist, status.HTTP_200_OK




@api.route("/api/verify")
def ApiVerify():
    """Verifies the existance of a twitter username by making a request though the webhost rather than Twitterself.
        Example request:
        /api/verify?username=realDonaldTrump&token=0r56766u
        Response:
        Returns false if name is taken -> exists
        Otherwise if not taken returns false
    """
    tok = request.args.get('token')
    username = request.args.get('username')
    if apiut.checktoken(tok) == False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN
    if username == "":
        error = {'Invalid_Username': 'True'}
        return error, status.HTTP_400_BAD_REQUEST
    r = requests.get('https://twitter.com/users/username_available?username=' + username )
    print(r)

    data = r.json()

    return data



@api.route("/api/<author>/updateauthordata", methods=['POST', 'GET'])
def ApiUpdateAuthorData(author):
    """
    Requests fresh author data from twitter and adds to the db.

    """
    tok = request.args.get('token')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN

    author = Author.query.filter_by(handle=author).first()

    if author is None:
        error = {'Author Exists': 'False'}
        return error, status.HTTP_400_BAD_REQUEST


    flash("Got your request! Expect the Author Data to be updated soon.", 'success')
    apiut.GetAuthorData(author)

    Forward = request.args.get("next")
    render_template("index.html")
    if Forward:
        return redirect(Forward)
    else:
        return redirect(url_for('misc.index'))



############################################################################################################################
# Additional functions left over from testing which I don't want to delete just yet :P

@api.route("/supersecreturl/creditadd")
def APITEMP():
    db.create_all()

    #author_1 = Author(id=1086397448304630020, handle="couplesdynamic2", screenname="Couples Dynamicd", bio="", joindatetime=dt, followertot=23, followingtot=72,liketot=543, mediatot=0, verified=0, private=0, avatar="https://openclipart.org/image/2400px/svg_to_png/277087/Female-Avatar-3.png")
    current_user.credits = 5

    db.session.commit()

    return redirect(url_for('webapp.scraper'))


"""
@api.route("/api/data/temp")
def temp():
    tok = request.args.get('token')

    if tok is None or apiut.checktoken(tok) ==False:
        error = {'Token_Verification': 'False'}
        return error, status.HTTP_403_FORBIDDEN

    dataout = User.query.all()
    if dataout is None:
        error = {'Users_Exists': 'False'}
        return error, status.HTTP_400_BAD_REQUEST
    final=[]
    for item in dataout:
        json_data = ut.Build_JSON_User(item)
        final.append(json_data)

    return final, status.HTTP_200_OK
"""



############################################################################################################################
