from flask import Blueprint, app, request, session, render_template
from flask.helpers import url_for
from werkzeug.utils import redirect
from medium_web import mysql

auth = Blueprint("auth", __name__, template_folder="template")


@auth.route("/")
@auth.route("/", methods=["GET", "POST"])
def me():

    cursorr = mysql.connection.cursor()
    cursorr.execute("Select * FROM postt")
    posts = cursorr.fetchall()

    cursorr.execute("select * from User")
    user_info_author = cursorr.fetchall()
    if "id" in session:
        return render_template(
            "home.html", posts=posts, user_info_author=user_info_author
        )

    return render_template("base.html", posts=posts, user_info_author=user_info_author)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM User WHERE email = %s", (email,))

        j = cur.fetchone()
        id = j[0]
        if j[1] == email and j[2] == password:
            session["id"] = id

            session.permanent = True
            mysql.connection.commit()
            cur.close()

        return redirect(url_for("auth.me"))
    return render_template("login.html")


# @auth.route("/")
# def medium():
#     if "id" not in session:
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT * FROM postt")
#         posts = cursor.fetchall()
#         return render_template("base.html", posts=posts)
#     else:
#         return render_template(url_for("auth.home"))


# @auth.route("/home")
# def home():
#     if "id" in session:
#         cursor = mysql.connection.cursor()
#         cursor.execute("SELECT * FROM postt")
#         posts = cursor.fetchall()
#         return render_template("home.html", posts=posts)
