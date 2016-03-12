import sqlite3
from flask import Flask, render_template, jsonify, request
from flask.ext.triangle import Triangle
from flask.ext.sqlalchemy import SQLAlchemy
from contextlib import closing
import config
import json

app = Flask(__name__)
app.config.from_object(config)
Triangle(app)
db = SQLAlchemy(app)

import commands
from models import *

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/messages", methods=["GET"])
def get_messages():
    return json.dumps([x.as_dict() for x in Message.query.all()])

@app.route("/api/command", methods=["POST"])
def handle_command():
    commands.handle_command(request.form["command"], "")
    return request.form["command"]

@app.route("/partials/<name>")
def get_partial(name):
    return render_template(name)

if __name__ == "__main__":
    app.run()
