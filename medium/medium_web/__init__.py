from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)


def create_app():

    app.secret_key = "abc"
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "martin"
    app.config["MYSQL_PASSWORD"] = "Vinayak++18"
    app.config["MYSQL_DB"] = "employees"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.jinja_env.add_extension("jinja2.ext.loopcontrols")

    from .auth import auth
    from .view import view

    auth = app.register_blueprint(auth, url_prefix="/")
    view = app.register_blueprint(view, url_prefix="/")

    return app


mysql = MySQL(app)
