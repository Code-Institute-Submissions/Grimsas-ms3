import os
from flask import (Flask, flash, render_template,redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_products")
def get_products():
    products = mongo.db.products.find()
    return render_template("products.html", products=products)


@app.route("/get_users")
def get_users():
    users = mongo.db.users.find()
    return render_template("users.html", users=users)


@app.route("/get_product_image")
def get_product_image():
    get_product_image = mongo.db.products.find()
    return render_template("get_product_image.html", get_product_image=get_product_image)


@app.route('/add_products')
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
