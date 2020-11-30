import os
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
# from flask_uploads import UploadSet, IMAGES
from bson.objectid import ObjectId
from wtforms import (StringField, PasswordField,
                     BooleanField, TextAreaField, SelectField)
from wtforms.validators import InputRequired, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import (LoginManager, UserMixin,
                         login_user, login_required, logout_user, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
if os.path.exists('env.py'):
    import env


app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

mongo = PyMongo(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login'
login_manager.login_message = u'Please log in to access this page.'

# images = UploadSet('images', IMAGES)

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
        InputRequired(), Length(min=5, max=20)])
    password = PasswordField('Password', [InputRequired()])

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(),
        Length(min=5, max=20,
               message='Username must be between 5 and 20 characters long')])
    password = PasswordField('New Password', [InputRequired(), EqualTo(
        'confirm', message='Passwords must match'),
        Length(min=8, max=80,
               message='password must be minimum 8 characters long')])
    confirm = PasswordField('Repeat Password')

class ReviewForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    category = SelectField('Category', choices=[(
        'first', 'First'), ('second', 'Second'), ('third', 'Third')])
    brand = StringField('Brand', validators=[InputRequired()])
    review = TextAreaField('Your Story')
    accept_tnc = BooleanField('I accept the T&C',
                              validators=[InputRequired()]),
    # upload = FileField('image', FileAllowed(images, 'Images only!'))


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
        print(user_exists)
        print(list(users.find()))
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
        print(user)
        if user is None or not check_password_hash(
                user['password'], form.password.data):
            flash('Invalid username or password')
            print(check_password_hash(
                user['password'], form.password.data))
            return redirect(url_for('login'))
        auth_user = User(user)
        login_user(auth_user)
        return redirect(url_for(
            "profile", username=current_user.user_session['username']))
    return render_template('login.html', form=form, action=action)


@app.route('/post_review', methods=['GET', 'POST'])
def post_review():
    post_review = ReviewForm()
    if post_review.validate_on_submit():
        confim_post = {
            'username': post_review.username.data,
            'caregory': post_review.category.data,
            'brand': post_review.brand.data,
            'review': post_review.review.data,
            'accept_tnc': post_review.accept_tnc.data,
            # 'upload': post_review.upload.data,
        }
        return render_template('confirm_post.html', **confim_post)
    return render_template('post_review.html', post_review=post_review)


@app.route('/get_categories')
def get_categories():
    categories = list(mongo.db.categories.find().sort('category_name', 1))
    return render_template('categories.html', categories=categories)

@app.route('/administrator')
@login_required
def administrator():
    return '<p>Hello {}</p>'.format(current_user.user_session['username'])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_products'))


if __name__ == '__main__':
    app.run(debug=True)
