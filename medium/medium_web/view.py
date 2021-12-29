import re
from flask import Blueprint, app, request, session, render_template
from flask.helpers import url_for
from werkzeug.utils import redirect
from medium_web import mysql

from base64 import b64encode
from datetime import date

view = Blueprint("view", __name__, template_folder="template")


@view.route("/write_blogg")
def write_bloggg():

    return redirect(url_for("auth.login"))


@view.route("/write_blog", methods=["POST", "GET"])
def write_blog():
    if "id" in session:
        print("llllllll")
        if request.method == "POST":

            title = request.form["title"]
            description = request.form["description"]
            info = request.form["info"]
            image = request.files["image"]
            img = image.read()
            author = "vk"
            today = date.today()
            print(today)

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT into postt (title,info,author,description,user_id,img,Date) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (title, info, author, description, 1, img, today),
            )

            mysql.connection.commit()
            cur.close()

            return redirect(url_for("auth.home", user_id=session["id"]))
        return render_template("write.html")
    return redirect(url_for("auth.login"))


@view.route("/view_post/<post_title>", methods=["GET", "POST"])
def view_post(post_title):
    print(id)
    post_title.replace("%20", " ")

    cur = mysql.connection.cursor()
    cur.execute("Select * from postt where title = %s", [post_title])
    post = cur.fetchone()
    post_img = post[6]

    image = b64encode(post_img).decode("utf-8")

    cur.execute("SELECT * FROM comment ")
    com = cur.fetchall()

    cur.execute("SELECT * FROM User ")
    user = cur.fetchall()
    mysql.connection.commit()
    cur.close()

    return render_template(
        "view_post.html", post=post, id=id, comments=com, user=user, img=image
    )
