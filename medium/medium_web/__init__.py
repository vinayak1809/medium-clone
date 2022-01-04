from re import A
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)


def create_app():
    app.config.from_object("config.DevelopmentConfig")

    app.jinja_env.add_extension("jinja2.ext.loopcontrols")

    from .auth import auth
    from .view import view

    auth = app.register_blueprint(auth, url_prefix="/")
    view = app.register_blueprint(view, url_prefix="/")

    return app


mysql = MySQL(app)
