import secrets
import os

from threading import Thread

from flask import url_for, current_app, render_template
from flask_mail import Message
from SA import mail, executor

from PIL import Image


@executor.job
def Email_Account_Creation(user):
    message = Message(subject="SA - Account Creation", sender='chenrymatthews@gmail.com', recipients=[user.email])
    message.html = render_template('/emails/html/account_creation.html', username=user.username)
    message.body = f'''Thanks for signing up to SA. To verify your email click here:
{url_for('users.verify',  _external=True)}
'''
    #FINISH HTML TEMPLATES
    mail.send(message)

@executor.job
def Email_Account_Verification(user):
    token = user.generate_token()
    message = Message(subject="SA - Account Verification", sender='chenrymatthews@gmail.com', recipients=[user.email])
    message.html = render_template('/emails/html/account_verify.html', username=user.username, token=token)
    message.body = f'''To verify your account, visit the following link:
{url_for('users.reset_confirm', token=token, _external=True)}
'''
    mail.send(message)

@executor.job
def Email_Password_Reset(user):
    token = user.generate_token()
    message = Message(subject="SA - Password Reset", sender='chenrymatthews@gmail.com', recipients=[user.email])
    message.html = render_template('/emails/html/password_reset.html', username=user.username, token=token)

    message.body = f'''To reset your password, visit the following link:
{url_for('users.reset_confirm', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    #FINISH HTML TEMPLATES
    mail.send(message)



def save_user_avatar(user_avatar):
    """
    Generates a random filename
    Resizes Image to 200x200 thumbnail
    Saves image to avatar static images
    Returns Filename to be stored in DB
    """
    RandomFileName = secrets.token_urlsafe(10)
    av, extension = os.path.splitext(user_avatar.filename)
    Avatar_FN = RandomFileName + extension
    Save_File_Path = os.path.join(current_app.root_path, "static/images/user_avatars", Avatar_FN)
    size = (200, 200)
    Avatar = Image.open(user_avatar)
    Avatar.thumbnail(size)
    Avatar.save(Save_File_Path)
    return Avatar_FN
