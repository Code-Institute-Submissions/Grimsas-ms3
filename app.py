import os
import json
import math
from flask import (Flask, flash, redirect, render_template, request, url_for)
from flask_pymongo import PyMongo, pymongo
from flask_wtf import FlaskForm
from bson.objectid import ObjectId
from bson import json_util
from bson.json_util import dumps
from wtforms import (StringField, PasswordField,
                     BooleanField, TextAreaField, SelectField, SubmitField)
from wtforms.validators import InputRequired, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import (LoginManager, UserMixin,
                         login_user, login_required, logout_user, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists('env.py'):
    import env


app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'




class User(UserMixin):
    def __init__(self, user_session):
        self.user_session = user_session

    def get_id(self):
        return self.user_session['user_cookie']


@login_manager.user_loader
def load_user(user_cookie):
    user_session = mongo.db.users.find_one({'user_cookie': user_cookie})
    if user_session:
        return User(user_session)
    return None

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(), Length(min=5, max=30)])
    password = PasswordField('Password', [InputRequired()])

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(),
        Length(min=5, max=30,
               message='Username must be between 5 and 30 characters long')])
    password = PasswordField('Password', [InputRequired(), EqualTo(
        'confirm', message='Passwords must match'),
        Length(min=8, max=80,
               message='password must be minimum 8 characters long')])
    confirm = PasswordField('Repeat Password')

class ReviewForm(FlaskForm):
    category = SelectField('Category',
                           choices=list(mongo.db.categories.find()))
    brand = StringField('Brand', validators=[InputRequired()])
    review = TextAreaField('Your Story', validators=[InputRequired()])
    accept_tnc = BooleanField('I accept the T&C',
                              validators=[InputRequired()]),
    title = StringField('Title', validators=[InputRequired()])



@app.route('/')
@app.route('/get_products')
def get_products():
    products = mongo.db.products.find()
    return render_template('index.html', products=products)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    action = 'signup'
    form = SignupForm()
    if request.method == 'POST' and form.validate():
        users = mongo.db.users
        user_exists = users.find_one(
            {'username': form.username.data})
        if user_exists is None:
            users.insert_one(
                ({'username': form.username.data,
                  'password': generate_password_hash(form.password.data),
                  'user_cookie': generate_password_hash(form.username.data)}))
            flash('Welcome!')
            return redirect(url_for('login'))

        flash('Username already exists! Try again')
        return redirect(url_for('signup'))
    return render_template('register.html', form=form, action=action)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    action = 'login'
    if form.validate_on_submit():
        users = mongo.db.users
        user = users.find_one({'username': form.username.data})
        if user is None or not check_password_hash(
                user['password'], form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        auth_user = User(user)
        login_user(auth_user)
        return redirect(url_for(
            'profile', username=current_user.user_session['username']))
    return render_template('login.html', form=form, action=action)


@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    username = current_user.user_session['username']
    if username:
        return render_template('profile.html', username=username)
    return redirect(url_for('login'))


# @app.route('/post_review', methods=['GET', 'POST'])
# def post_review():
#     return render_template("post_review.html",
#                            categories=mongo.db.categories.find(),
#                            products=mongo.db.products.find(),
#                            brands=mongo.db.brands.find(),
#                            users=mongo.db.users.find())


@app.route('/post_review', methods=['GET', 'POST'])
def post_review():
    action = 'post_review'
    post_review = ReviewForm()
    categories = list(mongo.db.categories.find())
    products = mongo.db.products.find()
    if post_review.validate_on_submit():
        confim_post = {
            'username': post_review.username.data,
            'caregory': post_review.category.data,
            'brand': post_review.brand.data,
            'review': post_review.review.data,
            'accept_tnc': post_review.accept_tnc.data
            # 'upload': post_review.upload.data,
        }
        return render_template('confirm_post.html', **confim_post)
    return render_template('post_review.html',
                           post_review=post_review,
                           action=action, categories=categories,
                           products=products)

# @app.route('/post_review', methods=['GET', 'POST'])
# def post_review_tags():
#     action = 'post_review_tags'
#     post_review_tags = ReviewFormTags()
#     if post_review_tags.validate_on_submit():
#         tags = {
#             'skintype': ['Normal', 'Oily', 'Dry',
#                          'Conbination', 'Sensitive', 'Mature'],
#             'pigmentation': ['Highly Pigmented', 'High Coverage',
#                              'Medium Coverage', 'Sheer', 'Buildable'],
#             'finish': ['Matte', 'Dewy', 'Satin', 'Glossy'],
#             'suggested_ocasions': ['Normal', 'Oily', 'Dry',
#                                    'Conbination', 'Sensitive', 'Mature']
#         }
#         return render_template('confirm_post.html', **tags)
#     return render_template('post_review.html',
#                            post_review_tags=post_review_tags, action=action)

@app.route("/uploads")
def upload(filename):
    return mongo.send_file(filename)

@app.route("/uploads/<filename>", methods=["POST"])
def download(filename):
    mongo.save_file(filename, request.files["file"])
    return redirect(url_for("uploads", filename=filename))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print(request.form.getlist('mycheckbox'))
        return redirect(url_for('get_products'))
    return render_template('index.html')


@app.route('/get_categories')
def get_categories():
    categories = list(mongo.db.categories.find())
    return render_template('categories.html', categories=categories)

@app.route('/admin/admin/', methods=['GET', 'POST'])
@login_required
def administrator():
    username = current_user.user_session['username']
    if username == 'administrator':
        return '<p>Hello {}</p>'.format(current_user.user_session['username'])
    flash('YOU SHALL NOT PASS')
    return redirect(url_for('get_products'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_products'))


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
