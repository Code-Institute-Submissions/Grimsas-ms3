import os
from bson.objectid import ObjectId
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash, generate_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def get_products():
    products = mongo.db.products.find()
    return render_template("index.html", products=products)


@app.route("/users")
def get_users():
    users = mongo.db.users.find()
    return render_template("users.html", users=users)


@app.route("/register")
def register():
    register = mongo.db.users.find()
    return render_template("register.html", register=register)


# @app.route("/get_product_image")
# def get_product_image():
#     get_product_image = mongo.db.products.find()
#     return render_template(
#         "get_product_image.html",
#         get_product_image=get_product_image)


@app.route('/add_your_grail')
def add_products():
    return render_template(
        'add_product.html', products=mongo.db.products.find())


@app.route("/get_latest")
def get_latest():
    latest = mongo.db.products.find().sort([('timestamp', -1)]).limit(1)
    return render_template("latetst.html", latetst=latest)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")),
            debug=True)
