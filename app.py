from flask import Flask
app = Flask(__name__)


@app.route("/")
def index():
    return "Home page"


@app.route("/login")
def login():
    return "You are not logged in!"
