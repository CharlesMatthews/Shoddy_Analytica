from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

webapp = Blueprint('webapp', __name__)

from SA import executor, db
from SA.models import Tweet, Author
import SA.utils as ut
import SA.webapp.webapp_utils as webut


import requests

@webapp.route("/app")
@login_required
def dashboard():
    """Main data dashboard - mashup of all data on system + general stats"""
    if ut.sessiongen(True) == False:
        return redirect(url_for('misc.index'))

    CPU, MEM, UserTot, TweetTot, AuthorTot, DataTot = ut.getstats()
    aclist = webut.Get_Account_List("app")

    RANDOM = webut.Get_Random_Three("*")
    TOP3 = webut.Get_Top_Three("*")
    RECENT3 = webut.Get_Recent_Three("*")



    return render_template("/webapp/webapp.html",RANDOM=RANDOM, TOP3= TOP3, RECENT3=RECENT3 ,CPU = CPU, MEM = MEM, UserTot = UserTot, TweetTot = TweetTot, AuthorTot = AuthorTot, DataTot = DataTot, ACLIST=aclist)


@webapp.route("/app/<handle>")
@login_required
def AuthorPage(handle):
    if ut.sessiongen(True) == False:
      return redirect(url_for('index'))
    """Author "dashboard" returns similar data to dashboard but more account specific"""

    data = Author.query.filter_by(handle=handle).first()

    if data is None:
        flash("The requested author does not exist.", 'danger')
        return redirect(url_for('misc.index'))

    RANDOM = webut.Get_Random_Three(handle)
    TOP3 = webut.Get_Top_Three(handle)
    RECENT3 = webut.Get_Recent_Three(handle)
    trained=False
    if handle == "realdonaldtrump":
        trained = True
    return render_template("/webapp/author.html",data = data, RANDOM=RANDOM, TOP3= TOP3, RECENT3=RECENT3, trained=trained)




@webapp.route("/app/<author>/tweets")
@login_required
def AuthorTweetsPage(author):

    """Author Tweets page - allows all tweets of an author to be viewed through the magic of JS"""
    if ut.sessiongen(True) == False:
      return redirect(url_for('misc.index'))

    if author != "*":
        author = Author.query.filter_by(handle=author).first()
        if author is None:
            flash("The requested author does not exist.", 'danger')
            return redirect(url_for('misc.index'))
        author = author.handle
    else:
        author = "*"

    return render_template("/webapp/tweetspage.html", Author = author)





@webapp.route("/search")
@login_required
def search():
    """Search page - returns results for either Tweets / Accounts"""
    ut.sessiongen(True)

    query = request.args.get('search')

    query = "%"+ query + "%"

    param = request.args.get('parameter')

    if param == "account":
        data =  Author.query.filter(Author.handle.like(query)).all()
    else:
        data = Tweet.query.filter(Tweet.text.like(query)).all()

    return render_template("/webapp/search.html", data=data, param=param)




@webapp.route("/aclist")
@login_required
def aclist():
    """
    Displays list of scraped Accounts within the database
    """
    ut.sessiongen(True)
    aclist = webut.Get_Account_List("aclist")


    return render_template("/webapp/aclist.html", aclist= aclist)



@webapp.route("/scraper", methods= ["GET", "POST"])
@login_required
def scraper():
    """
    Scraper page - allows users to be scrape either an account or a twitter query
    """
    ut.sessiongen(True)

    if request.method == 'POST':
        if current_user.credits <= 0:
            flash("Insufficient Credits to use the scraper.", 'danger')
            return redirect(url_for('webapp.scraper'))
        else:
            query = request.form.get("Query")
            hdl = request.form.get("Handle")

            if query is not None:
                flash("Thanks! We've received your request for scraping // '" +str(query) + "' //. Expect an email from us shortly! 👀", 'info')
                current_user.credits -= 1
                webut.Twint_Scrape_Query.submit(query, current_user)
                #webut.Twint_Scrape_Query(query, current_user)
            else:
                r = requests.get('https://twitter.com/users/username_available?username=' + hdl )
                data = r.json()
                if (data["msg"] == "Available!" or data["msg"] == "Username is too short" or data["msg"] == "Username is too long"):
                    flash("Invalid Account! :(", 'warning')
                else:
                    flash("Thanks! We've received your request for scraping @" +str(hdl) + ". Expect an email from us shortly! 👀", 'info')
                    current_user.credits -= 1

                    webut.Twint_Scrape_Account.submit(hdl, current_user)
                    #webut.Twint_Scrape_Account(hdl, current_user)

            db.session.commit()
            return redirect(url_for('webapp.scraper'))

    return render_template("/webapp/scraper.html")
