import re
from flask import Blueprint, app, request, session, render_template
from flask.helpers import url_for
from werkzeug.utils import redirect
from medium_web import mysql
from .auth import login_required
from base64 import b64encode
from datetime import date

view = Blueprint("view", __name__, template_folder="template")


@view.route("/<user_id>/write_blog", methods=["POST", "GET"])
@login_required
def write_blog(user_id):
    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        info = request.form["info"]
        image = request.files["image"]

        cur = mysql.connection.cursor()
        author = cur.execute("SELECT username FROM User WHERE id = %s", [user_id])
        today = date.today()

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT into postt (title,info,author,description,user_id,Date) VALUES (%s,%s,%s,%s,%s,%s)",
            [title, info, author, description, user_id, today],
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("auth.home", user_id=session["id"]))
    return render_template("write.html", user_id=session["id"])


@view.route("/view_post/<post_title>", methods=["GET", "POST"])
@login_required
def view_post(post_title):
    id = session["id"]
    post_title.replace("%20", " ")

    cur = mysql.connection.cursor()
    cur.execute("Select * from postt where title = %s", [post_title])
    post = cur.fetchone()

    try:
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

    except TypeError:
        cur.execute("SELECT * FROM comment ")
        com = cur.fetchall()

        cur.execute("SELECT * FROM User ")
        user = cur.fetchall()
        mysql.connection.commit()
        cur.close()

        return render_template(
            "view_post.html", post=post, id=id, comments=com, user=user
        )


@view.route("/like_post/<post_id>", methods=["GET"])
def like_post(post_id):

    cur = mysql.connection.cursor()
    cur.execute(
        "select * from Likee where (post_id_fk = %s and user_id_fk=%s)",
        (int(post_id), (session["id"])),
    )
    m = cur.fetchall()

    if m:
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE from Likee where (post_id_fk = %s and user_id_fk=%s)",
            (post_id, (session["id"])),
        )
        mysql.connection.commit()
        cur.close()

    else:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO Likee (user_id_fk,post_id_fk) VALUES(%s,%s)",
            (session["id"], int(post_id)),
        )
        mysql.connection.commit()
        cur.close()

        return redirect(request.referrer)

    return redirect(url_for("auth.home", user_id=session["id"]))


@view.route("/comment/<user_id>/<post_id>", methods=["POST", "GET"])
def comment(user_id, post_id):
    if request.method == "POST":
        print(user_id)
        cmmt = request.form["cmmt"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO comment (text,author_id,post_id) VALUES (%s,%s,%s) ",
            [cmmt, user_id, post_id],
        )

        mysql.connection.commit()
        cur.close()

        return redirect(request.referrer)

    return "ds"


@view.route("/delete_post/<post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM postt WHERE id =(%s)", [post_id])
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("auth.home", user_id=session["id"]))
