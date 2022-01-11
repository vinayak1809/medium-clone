from re import A
from flask import Flask
from flask_mysqldb import MySQL
from flask_mail import Mail

app = Flask(__name__)
app.config["TESTING"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = ""
app.config["MAIL_PASSWORD"] = ""
app.config["MAIL_MAX_EMAILS"] = None
app.config["MAIL_ASCII_ATTACHMENTS"] = False
app.config["DEFAULT_MAIL_SENDER"] = ""


def create_app():
    app.config.from_object("config.DevelopmentConfig")

    app.jinja_env.add_extension("jinja2.ext.loopcontrols")

    from .auth import auth
    from .view import view

    auth = app.register_blueprint(auth, url_prefix="/")
    view = app.register_blueprint(view, url_prefix="/")

    return app


mysql = MySQL(app)
mail = Mail(app)
