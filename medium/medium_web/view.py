
from flask import Blueprint, request, render_template, g
from flask.helpers import url_for
from werkzeug.utils import redirect
from medium_web import mysql, mail
from .auth import login_required, user as us
from flask_mail import Mail, Message

from base64 import b64encode
from datetime import date

view = Blueprint("view", __name__, template_folder="template")


@view.route("/u/<user_profile>", methods=["POST", "GET"])
@login_required
def user_profile(user_profile):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM User WHERE username = (%s)", [user_profile])
    user_info = cursor.fetchone()
    mysql.connection.commit()
    cursor.close()

    img = user_info[5]
    if img:
        image = b64encode(img).decode("utf-8")
        return render_template("user_profile.html", user=user_info, image=image)

    return render_template("user_profile.html", user=user_info)


@view.route("/<user_id>/write_blog", methods=["POST", "GET"])
@login_required
def write_blog(user_id):
    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        info = request.form["info"]
        image = request.files["image"]
        img = image.read()
        cur = mysql.connection.cursor()
        author = cur.execute(
            "SELECT username FROM User WHERE id = %s", [user_id])
        today = date.today()

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT into postt (title,info,author,description,user_id,img,Date) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            [title, info, author, description, user_id, img, today],
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for("auth.home", user_id=g.user))
    return render_template("write.html", user_id=g.user)


@view.route("/view_post/<post_title>", methods=["GET", "POST"])
@login_required
def view_post(post_title):

    post_title.replace("%20", " ")

    cur = mysql.connection.cursor()
    cur.execute("Select * from postt where title = %s", [post_title])
    post = cur.fetchone()

    try:
        cur.execute(
            "Select * from Like_post where post_id_fk = (%s)", [post[0]])
        like_post = cur.fetchall()
    except:
        like_post = ""
    try:
        post_img = post[6]
        image = b64encode(post_img).decode("utf-8")

        cur.execute("SELECT * FROM comment WHERE post_id = (%s)", [post[0]])
        com = cur.fetchall()

        return render_template(
            "view_post.html",
            post=post,
            id=g.user,
            comments=com,
            user=us(),
            img=image,
            like_post=like_post
        )

    except TypeError:
        cur.execute("SELECT * FROM comment ")
        com = cur.fetchall()

        return render_template(
            "view_post.html", post=post, id=g.user, comments=com, user=us(), like_post=like_post
        )


@view.route("/delete_post/<post_id>", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM postt WHERE id =(%s)", [post_id])
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("auth.home", user_id=g.user))


@view.route("/fav_post/<post_id>", methods=["GET"])
@login_required
def fav_post(post_id):

    cur = mysql.connection.cursor()
    cur.execute(
        "select * from favourite where (post_id_fk = %s and user_id_fk=%s)",
        (int(post_id), (g.user)),
    )
    m = cur.fetchall()

    if m:
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE from favourite where (post_id_fk = %s and user_id_fk=%s)",
            (post_id, (g.user)),
        )
        mysql.connection.commit()
        cur.close()

    else:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO favourite (user_id_fk,post_id_fk) VALUES(%s,%s)",
            (g.user, int(post_id)),
        )
        mysql.connection.commit()
        cur.close()

        return redirect(request.referrer)

    return redirect(url_for("auth.home", user_id=g.user))


@view.route("/like_post/<post_id>", methods=["GET"])
@login_required
def like_post(post_id):

    cur = mysql.connection.cursor()
    cur.execute(
        "select * from Like_post where (post_id_fk = %s and user_id_fk=%s)",
        (int(post_id), (g.user)),
    )
    m = cur.fetchall()

    if m:
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE from Like_post where (post_id_fk = %s and user_id_fk=%s)",
            (post_id, (g.user)),
        )
        mysql.connection.commit()
        cur.close()

    else:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO Like_post (user_id_fk,post_id_fk) VALUES(%s,%s)",
            (g.user, int(post_id)),
        )
        mysql.connection.commit()
        cur.close()

    return redirect(request.referrer)


@view.route("/comment/<user_id>/<post_id>", methods=["POST", "GET"])
@login_required
def comment(user_id, post_id):
    if request.method == "POST":

        cmmt = request.form["cmmt"]
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO comment (text,author_id,post_id) VALUES (%s,%s,%s) ",
            [cmmt, user_id, post_id],
        )

        mysql.connection.commit()
        cur.close()

        return redirect(request.referrer)

    return redirect(request.referrer)


@view.route("/delete_comment/<post_title>/<cmmt_id>", methods=["POST", "GET"])
@login_required
def delete_comment(post_title, cmmt_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM comment WHERE id= (%s)", [cmmt_id])
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("view.view_post", post_title=post_title))


@view.route("/<id>/update_profile", methods=["POST", "GET"])
@login_required
def update_profile(id):
    if request.method == "POST":
        about = request.form.get("about")
        image = request.files["image"]

        cursor = mysql.connection.cursor()
        print(image)
        print(about)
        if image:
            img = image.read()
            cursor.execute("UPDATE User SET user_img = %s, about=%s WHERE id= %s", [
                img, about, id])
        else:
            cursor.execute("UPDATE User SET  about=%s WHERE id= %s", [
                about, id])
        mysql.connection.commit()
        cursor.close()

        return redirect(request.referrer)

    return render_template("update_profile.html", id=id)


@view.route("/report/<post_id>")
@login_required
def report(post_id):
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT into report (user_id_fk,post_id_fk) VALUES(%s,%s)",
        [g.user, post_id],
    )
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("auth.home", user_id=g.user))


# -------------------------------------         admin section        -------------------------------------


@view.route("/email_post/<post_id>", methods=["POST", "GET"])
def email(post_id):

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from postt WHERE id = (%s)", [post_id])
    fetch = cursor.fetchall()

    cursor.execute("SELECT * from User where id = (%s)", [fetch[0][5]])
    user_fetch = cursor.fetchall()

    if request.method == "POST":
        title = request.form['title']
        email = request.form['email']
        message = request.form['message']
        subject = request.form['subject']

        msg = Message(
            title,  # post is being delete ,
            sender="",
            recipients=[email],  # receiver email
        )
        msg.body = message  # Body of the email to send
        mail.send(msg)

        cursor.execute("DELETE FROM postt WHERE id =(%s)", [post_id])
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("auth.admin"))
    return render_template("email.html", post=fetch, user_post=user_fetch, post_id=post_id)


@view.route("/email_user/<user_id>", methods=["POST", "GET"])
def email_user(user_id):

    cursor = mysql.connection.cursor()
    cursor.execute("Select * FROM User WHERE id = (%s)", [user_id])
    user_info = cursor.fetchall()

    if request.method == "POST":
        title = request.form['title']
        email = request.form['email']
        message = request.form['message']
        subject = request.form['subject']

        msg = Message(
            title,
            sender="",
            recipients=[email]  # email,
        )
        msg.body = message
        mail.send(msg)

        cursor.execute("DELETE FROM User WHERE id =(%s)", [int(user_id)])
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("auth.admin"))
    return render_template("email.html", user=user_info)
