from flask import render_template, request, redirect, url_for, session
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
from flask.helpers import flash
app = Flask(__name__)

app.config["IMAGE_UPLOADS"] = "C:/Users/SAB/Desktop/flask_app/IMAGE_UPLOADS/"
app.config["IMAGE_VERIFY"] = "C:/Users/SAB/Desktop/flask_app/IMAGE_VERIFY/"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '19BCI0105'
db = SQLAlchemy(app)


class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["pass"]
        if email != "" and password != "":
            login = user.query.filter_by(
                email=email, password=password).first()
            if login is not None:
                # account found
                session["user"] = login.username
                return redirect(url_for("image_verify"))
            else:
                # account not exist
                flash("account does not exist")
                return redirect(url_for("register"))
        else:
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/home")
def home():
    if "user" in session:
        user = session["user"]
        return render_template("home.html", user=user)
    else:
        return redirect(url_for("login"))


@app.route("/image-verification", methods=["GET", "POST"])
def image_verify():
    if "user" in session:
        user = session["user"]
        if request.method == "POST":
            if request.files:
                image = request.files["image"]
                img_type = image.filename.split(".")[1]
                if(img_type != "jpg"):
                    return redirect(url_for("login"))
                else:
                    image_name = "login.jpg"
                    image.save(os.path.join(
                        app.config["IMAGE_VERIFY"], image_name))
                    original_image_name = user + ".jpg"
                    original_image = cv2.imread(os.path.join(
                        app.config["IMAGE_UPLOADS"], original_image_name))
                    uploaded_image = cv2.imread(os.path.join(
                        app.config["IMAGE_VERIFY"], image_name))
                    if original_image.shape == uploaded_image.shape:
                        difference = cv2.subtract(
                            original_image, uploaded_image)
                        b, g, r = cv2.split(difference)
                        blue_colour_difference = cv2.countNonZero(b)
                        green_colour_difference = cv2.countNonZero(g)
                        red_colour_difference = cv2.countNonZero(r)
                        if blue_colour_difference == 0 and green_colour_difference == 0 and red_colour_difference == 0:
                            return redirect(url_for("home"))
                        else:
                            return redirect(url_for("login"))
                    else:
                        return redirect(url_for("login"))
        return render_template("image_verification.html")
    else:
        return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']
        if request.files:
            image = request.files["image"]
            img_type = image.filename.split(".")[1]
            if(img_type != "jpg"):
                # return redirect(url_for("register"))
                return img_type
            else:
                image_name = name + ".jpg"
                image.save(os.path.join(
                    app.config["IMAGE_UPLOADS"], image_name))

                newuser = user.query.filter_by(email=email).first()
                if newuser is None:
                    register = user(username=name, email=email,
                                    password=password)
                    db.session.add(register)
                    db.session.commit()
                    flash("user created successfully")
                    return redirect(url_for("login"))
                else:
                    flash("user already exists")
                    return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
