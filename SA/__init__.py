import os

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_executor import Executor


from flask_api import FlaskAPI

db = SQLAlchemy()
crypt = Bcrypt()
mail = Mail()
login_mgr = LoginManager()
executor = Executor()


login_mgr.login_view = "users.login"
login_mgr.login_message_category = "info"

def generate_app():
    app = FlaskAPI(__name__)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
    app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
    app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")
    app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS")
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['EXECUTOR_MAX_WORKERS'] = 4



    db.init_app(app)
    crypt.init_app(app)
    login_mgr.init_app(app)
    mail.init_app(app)
    executor.init_app(app)
    #api.init_app(app)

    with app.test_request_context():
        db.create_all()

    from SA.users.routes import users
    from SA.misc.routes import misc
    from SA.webapp.routes import webapp
    from SA.api.routes import api

    app.register_blueprint(users)
    app.register_blueprint(misc)
    app.register_blueprint(webapp)
    app.register_blueprint(api)

    return app
