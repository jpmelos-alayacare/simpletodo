import click
import bcrypt

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost/simpletodo'
db = SQLAlchemy(app)


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
        pw_hash=User.hash_password(password.encode('ascii')),
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
        return bcrypt.hashpw(password, bcrypt.gensalt())

    @classmethod
    def check_password(cls, password, pw_hash):
        return bcrypt.checkpw(password.encode('ascii'), pw_hash.encode('ascii'))


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.session.query(User).filter_by(
            username=request.form['username'],
        ).one_or_none()
        if user is not None:
            if User.check_password(request.form['password'], user.pw_hash):
		    return render_template(
		        'logged_in.html',
		        username=request.form['username'],
		    )

        return render_template('login.html', error=True)

    return render_template('login.html', error=False)
