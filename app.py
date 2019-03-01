import click
import bcrypt
from sqlalchemy import or_

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.secret_key = b'secret_key'

# Configure database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost/simpletodo'
db = SQLAlchemy(app)

# Configure login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(
        id=int(user_id),
    ).one_or_none()


@app.cli.command()
def initdb():
    db.create_all()


@app.cli.command()
@click.argument('username')
@click.argument('email')
@click.argument('password')
def createuser(username, email, password):
    user = User(
        username=username,
        email=email,
        pw_hash=User.hash_password(password),
    )
    db.session.add(user)
    db.session.commit()


class User(db.Model):
    __tablename__ = 'tbl_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash = db.Column(db.String(60), nullable=False)

    def __str__(self):
        return '<User {}>'.format(self.username)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    @classmethod
    def hash_password(cls, password):
        return bcrypt.hashpw(password.encode('ascii'), bcrypt.gensalt())

    @classmethod
    def check_password(cls, password, pw_hash):
        return bcrypt.checkpw(password.encode('ascii'), pw_hash.encode('ascii'))

    is_authenticated = True
    is_anonymous = False
    is_active = True

    def get_id(self):
        return unicode(self.id)


@app.route("/")
def index():
    return render_template('index.html', user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if '' in [username, email, password]:
            return render_template('register.html', error=True)

        # Also check that email is in a valid format

        if db.session.query(User).filter(or_(
            User.username == username,
            User.email == email,
        )).first() is not None:
            return render_template('register.html', error=True)

        user = User(
            username=username,
            email=email,
            pw_hash=User.hash_password(password),
        )
        db.session.add(user)
        db.session.commit()

        return render_template('register_success.html')

    return render_template('register.html', error=False)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        user = db.session.query(User).filter_by(
            username=request.form['username'],
        ).one_or_none()
        if user is not None:
            if User.check_password(request.form['password'], user.pw_hash):
                login_user(user)

                return render_template(
                    'logged_in.html',
                    username=request.form['username'],
                )

        return render_template('login.html', error=True)

    return render_template('login.html', error=False)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
