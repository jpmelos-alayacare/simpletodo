import click

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:root@localhost/simpletodo'
db = SQLAlchemy(app)


@app.cli.command()
def initdb():
    db.create_all()


class User(db.Model):
    __tablename__ = 'tbl_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __str__(self):
        return '<User {}>'.format(self.username)

    def __repr__(self):
        return '<User {}>'.format(self.username)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.session.query(User).filter_by(username=request.form['username']).one_or_none()
        if user is not None:
            return render_template(
                'logged_in.html',
                username=request.form['username'],
            )

        return render_template('login.html', error=True)

    return render_template('login.html', error=False)
