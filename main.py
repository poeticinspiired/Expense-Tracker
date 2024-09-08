from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulating a database with a dictionary
users = {}

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    app.logger.info(f"Loading user: {user_id}")
    user = users.get(user_id)
    if user:
        app.logger.info(f"User {user_id} loaded successfully")
    else:
        app.logger.warning(f"User {user_id} not found")
    return user

@app.route('/')
@login_required
def index():
    app.logger.info(f"Accessing index page. Current user: {current_user.username}")
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        app.logger.info(f"Attempting to register user: {username}")
        if username in users:
            app.logger.warning(f"Registration failed: Username {username} already exists")
            flash('Username already exists')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        user = User(id=username, username=username, password=hashed_password)
        users[username] = user
        app.logger.info(f"New user registered: {username}")
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info("Accessing login route")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        app.logger.info(f"Login attempt for user: {username}")
        user = users.get(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            app.logger.info(f"User {username} logged in successfully")
            next_page = request.args.get('next')
            app.logger.info(f"Next page requested: {next_page}")
            if not next_page or not is_safe_url(next_page):
                next_page = url_for('index')
            app.logger.info(f"Redirecting to: {next_page}")
            return redirect(next_page)
        else:
            app.logger.warning(f"Failed login attempt for user {username}")
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    app.logger.info(f"User {current_user.username} logged out")
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/current_time')
def get_current_time():
    return jsonify({'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/debug')
def debug():
    return jsonify({
        'users': [{'username': user.username, 'id': user.id} for user in users.values()],
        'current_user': current_user.username if current_user.is_authenticated else 'Not logged in'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)