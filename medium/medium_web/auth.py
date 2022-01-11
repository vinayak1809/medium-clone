import re
from flask import Blueprint, app, request, session, render_template, flash, g, wrappers
from functools import wraps
from PIL import Image

from flask.ctx import AppContext
from flask.helpers import url_for
from flask.json.tag import PassDict
from werkzeug.utils import redirect
from medium_web import mysql, mail
from flask_mail import Mail, Message
from datetime import date

from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode

auth = Blueprint("auth", __name__, template_folder="template")


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "id" in session:
            return f(*args, **kwargs)
        if "admin" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login", "danger")
            return redirect(url_for("auth.login"))

    return wrap


@auth.app_template_filter("make_caps")
def caps(text):
    texts = str(text)

    return texts.casefold()


def img():
    cursorr = mysql.connection.cursor()
    cursorr.callproc("select_post")
    posts = cursorr.fetchall()

    img_dic = {
        posts[i][0]: b64encode(posts[i][6]).decode("utf-8") if posts[i][6] else " "
        for i in range(0, len(posts))
    }

    return img_dic


def post():
    cursorr = mysql.connection.cursor()
    cursorr.callproc("select_post")
    posts = cursorr.fetchall()

    cursorr.close()
    return posts


def user():
    cursorr = mysql.connection.cursor()
    cursorr.execute("SELECT * FROM User ")
    user = cursorr.fetchall()

    cursorr.close()
    return user


def cmmt():
    cursorr = mysql.connection.cursor()
    cursorr.execute("SELECT * FROM comment ")
    cmmt = cursorr.fetchall()

    cursorr.close()
    return cmmt


def like_post():
    cursorr = mysql.connection.cursor()
    cursorr.execute("SELECT * FROM Likee ")
    like = cursorr.fetchall()

    cursorr.close()
    return like


@auth.route("/", methods=["GET", "POST"])
def base():
    if "id" not in session:
        cursorr = mysql.connection.cursor()
        cursorr.execute("Select * FROM postt")

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
        return render_template(
            "base.html",
            posts=post(),
            user_info_author=user(),
            img_dic=img(),
            li=li,
        )

    else:
        return redirect(url_for("auth.home", user_id=session["id"]))


@auth.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":

        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        today = date.today()

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT email FROM User WHERE email= %s", [email])
        email_exists = cursor.fetchall()

        cursor.execute("SELECT username FROM User WHERE username= %s", [username])
        username_exists = cursor.fetchall()
        session.pop("_flashes", None)
        if email_exists:
            flash("Email is already in use.", category="error")
        elif len(email) < 4:
            flash("Email is invalid.", category="error")
        elif username_exists:
            flash("Username is already in use.", category="error")
        elif len(username) < 2:
            flash("Username is too short.", category="error")
        elif len(password1) < 6:
            flash("Password is too short.", category="error")
        elif password1 != password2:
            flash("Password don't match!", category="error")

        else:

            password = generate_password_hash(password1, method="sha256")
            cursor.execute(
                "INSERT INTO User(email,password,username,date_created) VALUES(%s,%s,%s,%s)",
                [email, password, username, today],
            )
            mysql.connection.commit()
            cursor.close()
            flash("User created!", category="success")

            return redirect(url_for("auth.base"))

    return render_template("login.html", signup="Sign Up")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if "id" not in session:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM User WHERE email = %s", (email,))

            j = cur.fetchone()
            session.pop("_flashes", None)

            if j != None:
                if j[1][-9:] == "admin.com":
                    session["admin"] = "admin"
                    return redirect(url_for("auth.admin"))
                if check_password_hash(j[2], password):
                    if j[1] == email and check_password_hash(j[2], password):
                        id = j[0]
                        session["id"] = id
                        mysql.connection.commit()
                        cur.close()
                        return redirect(url_for("auth.home", user_id=id))
                else:
                    flash("wrong password", category="error")
            elif j == None:
                flash("wrong email", category="error")

            return render_template("login.html", signin="Sign In")

        return render_template("login.html", signin="Sign In")
    return redirect(url_for("auth.home", user_id=session["id"]))


@auth.route("/<path:user_id>", methods=["GET", "POST"])
@login_required
def home(user_id):
    if "id" in session:
        if user_id == str(session["id"]):

            cursorr = mysql.connection.cursor()
            cursorr.execute("select * from Likee where user_id_fk=%s", [user_id])
            like_in = cursorr.fetchall()
            li = [like_in[i][3] for i in range(len(like_in))]

            # image = b64encode(post_img).decode("utf-8")

            if "id" in session:
                return render_template(
                    "home.html",
                    posts=post(),
                    user_info_author=user(),
                    id=user_id,
                    li=li,
                    img_dic=img(),
                )

            else:
                return redirect(url_for("auth.base"))
        return redirect(url_for("auth.home", user_id=str(session["id"])))
    return redirect(url_for("auth.admin"))


@auth.route("/signout")
@login_required
def signout():
    session.pop("id", None)
    return redirect(url_for("auth.base"))


# -----------------------------------        admin section        --------------------------------------


@auth.route("/admin", methods=["POST", "GET"])
def admin():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM report")
    report = cursor.fetchall()
    li = [report[i][3] for i in range(len(report))]

    msg = Message(
        "mail title",
        sender="",
        recipients=[""],
    )
    msg.body = "Body of the email to send"

    mail.send(msg)

    if request.method == "POST":

        email_search = request.form.get("email_search")
        username_search = request.form.get("username_search")
        search_user_id = request.form.get("search_user_id")

        if email_search:
            cursor.execute("SELECT * FROM User WHERE email = (%s)", [email_search])
            fetch_email = cursor.fetchall()
            return render_template(
                "admin.html",
                posts=post(),
                img=img(),
                users=fetch_email,
            )

        elif username_search:
            cursor.execute(
                "SELECT * FROM User WHERE username = (%s)", [username_search]
            )
            fetch_username = cursor.fetchall()
            return render_template(
                "admin.html",
                posts=post(),
                img=img(),
                users=fetch_username,
            )
        elif search_user_id:
            cursor.execute("SELECT * FROM postt WHERE user_id = (%s)", [search_user_id])
            user_posts = cursor.fetchall()
            return render_template(
                "admin.html", img=img(), users=user(), posts=user_posts
            )

    return render_template(
        "admin.html", posts=post(), users=user(), img=img(), report=li
    )


@auth.route("/signout")
@login_required
def admin_signout():
    session.pop("admin", None)
    return redirect(url_for("auth.base"))


# @auth.route("/mail")
# def index():
#     msg = Message(
#         "mail title",
#         sender="shindevrcs19@student.mes.ac.in",
#         recipients=["vinayakrshinde18@gmail.com"],
#     )
#     msg.body = "Body of the email to send"

#     mail.send(msg)
#     return "Mail Sent..."


# @auth.errorhandler(404)
# def error(error):
#     return "page not found"


# @auth.teardown_request
# def teardown_request(error=None):
#     if error:
#         return "not found"
