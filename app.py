from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_talisman import Talisman
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from forms import LoginForm, RegistrationForm

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key in production

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Initialize the database and other extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Set up Flask-Talisman for security headers and HTTPS (in production)
csp = {
    'default-src': [
        '\'self\'',
        'https://cdnjs.cloudflare.com',
    ],
    'img-src': '*',
    'script-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
    ],
    'style-src': [
        '\'self\'',
        'https://cdn.jsdelivr.net',
    ]
}

Talisman(app, content_security_policy=csp)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(150), nullable=True)

# Route for the home page
@app.route('/')
def home():
    return "Welcome to the Online Bookstore!"

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data

        # Check if the username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists, please choose another one.')
            return redirect(url_for('register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists, please choose another one.')
            return redirect(url_for('register'))

        # Hash the password and save the new user to the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        # Log the user in and redirect to the dashboard
        session['username'] = username
        return redirect(url_for('dashboard'))

    return render_template('register.html', form=form)

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query the user from the database
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            session.permanent = True
            session.modified = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

# Route for the dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        return render_template('dashboard.html', username=session['username'], user=user)
    return redirect(url_for('login'))

# Route for the profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        user.email = request.form['email']
        user.bio = request.form['bio']

        if 'profile_pic' in request.files:
            pic = request.files['profile_pic']
            filename = secure_filename(pic.filename)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            user.profile_pic = filename

        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    cover_image = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return f'<Book {self.title}>'

@app.route('/books')
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

@app.route('/add_to_cart/<int:book_id>')
def add_to_cart(book_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(book_id)
    flash('Book added to cart')
    return redirect(url_for('books'))

@app.route('/cart')
def cart():
    if 'cart' not in session or len(session['cart']) == 0:
        flash('Your cart is empty')
        return redirect(url_for('books'))
    
    cart_books = Book.query.filter(Book.id.in_(session['cart'])).all()
    return render_template('cart.html', books=cart_books)













 






