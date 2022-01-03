from flask import Blueprint, app, request, session, render_template, flash
from functools import wraps
from flask.helpers import url_for
from werkzeug.utils import redirect
from medium_web import mysql

from base64 import b64encode

auth = Blueprint("auth", __name__, template_folder="template")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "id" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login", "danger")
            return redirect(url_for("auth.login"))

    return wrap


@auth.route("/<user_id>", methods=["GET", "POST"])
@login_required
def home(user_id):
    if user_id == str(session["id"]):

        cursorr = mysql.connection.cursor()
        cursorr.callproc("select_post")
        posts = cursorr.fetchall()

        cursorr.execute("select * from Likee where user_id_fk=%s", [user_id])
        like_in = cursorr.fetchall()
        li = [like_in[i][3] for i in range(len(like_in))]

        img_dic = {
            posts[i][0]: b64encode(posts[i][6]).decode("utf-8") if posts[i][6] else " "
            for i in range(0, len(posts))
        }

        # image = b64encode(post_img).decode("utf-8")

        cursorr.execute("select * from User")
        user_info_author = cursorr.fetchall()

        if "id" in session:
            return render_template(
                "home.html",
                posts=posts,
                user_info_author=user_info_author,
                id=user_id,
                li=li,
                img_dic=img_dic,
            )

        else:
            return redirect(url_for("auth.base"))
    return redirect(url_for("auth.home", user_id=str(session["id"])))


@auth.route("/", methods=["GET", "POST"])
def base():
    if "id" not in session:
        cursorr = mysql.connection.cursor()
        cursorr.execute("Select * FROM postt")
        posts = cursorr.fetchall()

        li = [
            "Self",
            "Relationship",
            "Data Science",
            "Programming",
            "Productivity",
            "Javascript",
            "sports",
            "tech",
            "python",
            "stress",
            "Politics",
            "Health",
        ]

        img_dic = {
            posts[i][0]: b64encode(posts[i][6]).decode("utf-8") if posts[i][6] else " "
            for i in range(0, len(posts))
        }

        cursorr.execute("select * from User")
        user_info_author = cursorr.fetchall()
        return render_template(
            "base.html",
            posts=posts,
            user_info_author=user_info_author,
            img_dic=img_dic,
            li=li,
        )

    else:
        return redirect(url_for("auth.home", user_id=session["id"]))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if "id" not in session:
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

            return redirect(url_for("auth.home", user_id=id))
        return render_template("login.html")
    return redirect(url_for("auth.home", user_id=session["id"]))


@auth.route("/signout")
@login_required
def signout():
    session.pop("id", None)
    return redirect(url_for("auth.base"))


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
