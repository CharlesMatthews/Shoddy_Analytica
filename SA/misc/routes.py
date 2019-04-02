from flask import Blueprint, render_template
from flask_login import login_required

import SA.utils as ut

misc = Blueprint('misc', __name__)

@misc.route("/")
def index():
    """
    Homepage.
    """
    ut.sessiongen(False)
    return render_template("index.html")


@misc.route("/api")
@login_required
def api():
    """
    Page for API documentation.
    """
    if ut.sessiongen(True) == False:
      return redirect(url_for('misc.index'))
    return render_template("misc/api.html")

@misc.route("/about")
@login_required
def about():
    """
        About page of service.
    """
    if ut.sessiongen(True) == False:
      return redirect(url_for('misc.index'))
    return render_template("misc/about.html", title="About SA")


@misc.route("/stats")
@login_required
def stats():
    """
    Stats page for the service. Serverload + db etc.
    """
    if ut.sessiongen(True) == False:
      return redirect(url_for('misc.index'))
    CPU, MEM, UserTot, TweetTot, AuthorTot, DataTot = ut.getstats()

    return render_template("misc/stats.html", CPU = CPU, MEM = MEM, UserTot = UserTot, TweetTot = TweetTot, AuthorTot = AuthorTot, DataTot = DataTot)
