from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from WebBlog.db import User, Post, Category
from WebBlog.LoginRequired import login_required
# from api import list_post
import requests

blog_bp = Blueprint('blog', __name__)


@blog_bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.objects(id=user_id)[0]


@blog_bp.route('/')
@blog_bp.route('/home')
def home():
    if request.method == "GET":
        posts=[]
        for post in Post.objects:
            posts.append(post)
        return render_template("home.html", posts=posts)


@blog_bp.route("/signup/", methods=("GET", "POST"))
def sign_up():
    if request.method == "POST":
        username_form = request.form["username"]
        first_name_form = request.form["first_name"]
        last_name_form = request.form["last_name"]
        email_form = request.form["email"]
        phone_form = request.form["phone"]
        password_form = request.form["password"]
        password_form2 = request.form["password2"]
        error = None

        if not username_form:
            error = "Username is required."

        elif not password_form:
            error = "Password is required."

        elif password_form2 != password_form:
            error = "Passwords are not same !"

        elif len(password_form) < 8:
            error = "Can not be less than 8 characters"

        elif User.objects(username=username_form):
            error = f"User {username_form} is already registered."

        if not error:
            user_created = User(username=username_form,
                                email=email_form,
                                first_name=first_name_form,
                                last_name=last_name_form,
                                phone_number=phone_form,
                                password=generate_password_hash(password_form))
            user_created.save()

            return redirect(url_for("blog.login"))

        flash(error)
    return render_template('signup.html')


@blog_bp.route("/login/", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username_form = request.form["username"]
        password_form = request.form["password"]
        error = None
        if User.objects(username=username_form):
            current_user = User.objects(username=username_form)[0]
            if not check_password_hash(current_user.password, password_form):
                error = "Incorrect password."
        else:
            error = "Incorrect username."

        if error is None:
            session.clear()
            session["user_id"] = str(current_user.id)
            # print('hello1')
            return redirect(url_for("blog.home"))

        flash(error)
    return render_template("login.html")


@blog_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("blog.home"))


@blog_bp.route("/post/<post_id>")
def post():
    pass


@blog_bp.route("/category-posts/<category_id>")
def category(category_id):
    list_of_cats = [category_id]
    posts = []
    for cat in Category.objects:
        if cat.parent_cat:
            # print('this   ',str(cat.parent_cat.id))

            print('that', str(cat.id))
            if str(cat.parent_cat.id) in list_of_cats:
                # print('3')
                list_of_cats.append(str(cat.id))

    for post in Post.objects:
        if post.cat:
            if str(post.cat[0]) in list_of_cats:
                posts.append(post)
    return render_template("posts_list.html", posts=posts)


@blog_bp.route("/tag-posts/<tag_id>")
def tag(tag_id):
    # print(tag_id)
    # print(type(tag_id))
    posts = Post.objects(tags__in=[tag_id])
    # print(posts)
    return render_template("posts_list.html", posts=posts)


if __name__ == "__main__":
    for posts in Post.objects:
        img = posts['photo']
        print(img)
