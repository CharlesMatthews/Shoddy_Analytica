#!/usr/bin/python3

from flask import session, render_template, request, redirect, url_for, redirect, flash, Blueprint
from flask_login import login_user, current_user, logout_user, login_required


from SA.models import User
from SA.users.forms import Form_Register, Form_Login, Form_Update_Account, Form_Password_Request, Form_Reset_Password
from SA import db, crypt, executor

import SA.utils as ut
import SA.users.user_utils as userut

import secrets


users = Blueprint('users', __name__)


@users.route("/register", methods= ["GET", "POST"])
def register():
    ut.sessiongen(False)
    if current_user.is_authenticated:
        return redirect(url_for('misc.index'))
    form = Form_Register()
    if form.validate_on_submit():
        dbverification = True
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            dbverification= False
            flash("Email already in use - Please enter another and try again", 'danger')

        user = User.query.filter_by(username=form.username.data).first()
        if user:
            dbverification=False
            flash("username taken - Please choose another and try again", 'danger')
        if dbverification == True:
            password_hash = crypt.generate_password_hash(form.password.data).decode('utf-8')
            tok = secrets.token_urlsafe(30)
            user = User(username=form.username.data, email=form.email.data.lower(), password_hash=password_hash, token=tok, verified=0, credits=0)

            db.session.add(user)
            db.session.commit()
            userut.Email_Account_Creation.submit(user)

            flash(f"Registration Sucessful as {form.username.data}!", 'success')
            session["utoken"].append(user.token)
            return redirect(url_for('users.login'))
    return render_template("user/register.html", title="SA - Registration", form=form)


@users.route("/login", methods= ["GET", "POST"])
def login():
    ut.sessiongen(False)
    if current_user.is_authenticated:
        return redirect(url_for('misc.index'))
    form = Form_Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and crypt.check_password_hash(user.password_hash, form.password.data):
            session["utoken"].append(user.token)
            login_user(user, remember=form.rememberme.data)
            #print(user.token)
            flash(f"Logged in as {form.email.data.lower()}!", 'success')
            Forward = request.args.get("next")
            if Forward:
                return redirect(Forward)
            else:
                return redirect(url_for('misc.index'))
        else:
            flash(f"Login Failed - Please check your email and password", 'danger')
    return render_template("user/login.html", title="SA - Login", form=form)

@users.route("/logout", methods=['GET', 'POST'])
def logout():
    """
    Logs user out + Removes Token from user session
    """
    ut.sessiongen(False)
    logout_user()
    if session["utoken"] != []:
        session["utoken"] = []
        flash("Logged out sucessfully!", 'success')
    return redirect(url_for('misc.index'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    """
    User account page
    """
    ut.sessiongen(True)
    form = Form_Update_Account()
    if form.validate_on_submit():


        if form.avatar.data:
            current_user.avatar = userut.save_user_avatar(form.avatar.data)
        if form.username.data:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                flash("Failed to update Username - Already Taken!", "danger")
            else:
                current_user.username = form.username.data
        if form.email.data:
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user:
                flash("Failed to update email - Already in use!", "danger")
            else:
                current_user.email = form.email.data.lower()
        db.session.commit()
        flash("Account details updated sucessfully!", "success")
        return redirect(url_for("users.account"))
    return render_template("user/account.html", form=form)



@users.route("/reset", methods= ["GET", "POST"])
def reset():
    ut.sessiongen(False)
    if current_user.is_authenticated:
        return redirect(url_for('misc.index'))
    form = Form_Password_Request()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        userut.Email_Password_Reset.submit(user)
        flash("Thanks! - Expect an email from us shortly 👀", 'success')
        return redirect(url_for("misc.index"))
    return render_template("user/reset.html", title="SA - Login", form=form)


@users.route("/reset/<token>", methods= ["GET", "POST"])
def reset_confirm(token):
    ut.sessiongen(False)

    user = User.verify_token(token)

    if user:
            form = Form_Reset_Password()
            if form.validate_on_submit():
                dbverification = True
                password_hash = crypt.generate_password_hash(form.password.data).decode('utf-8')
                user.password_hash = password_hash
                db.session.commit()
                flash(f"Password updated sucessfully!", 'success')
                return redirect(url_for('users.login'))
    elif user is None:
        flash("Invalid or Expired Token", 'warning')
        return redirect(url_for("users.reset"))


    return render_template("user/reset_confirm.html", title="SA - Login", form=form)



@users.route("/verify", methods= ["GET", "POST"])
@login_required
def verify():
    ut.sessiongen(False)
    if current_user.verified ==1:
        flash("Account Already Verified", 'info')
        return redirect(url_for("misc.index"))
    else:
        user = current_user
        userut.Email_Account_Verification.submit(user)
        flash("Expect an email from us shortly! 👀", 'success')

    return redirect(url_for('misc.index'))


@users.route("/verify/<token>", methods= ["GET", "POST"])
def verify_confirm(token):
    ut.sessiongen(False)

    user = User.verify_token(token)

    if user is None:
        flash("Invalid or Expired Token", 'warning')
        return redirect(url_for('users.login'))


    if current_user.verified == 0:
        flash("Account verified!", 'success')
        current_user.credits = 5
        current_user.verified = True
        db.session.commit()
    else:
        flash("Already Verified", 'info')

    return redirect(url_for('misc.index'))
