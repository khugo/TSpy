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
    return render_template("base.html")

@app.route("/api/messages", methods=["GET"])
def get_messages():
    return json.dumps([x.as_dict() for x in Message.query.order_by("date desc")])

@app.route("/api/command", methods=["POST"])
def handle_command():
    header_str = request.form["header"]
    print("Got header " + header_str)
    header_bytes = []
    for byte in header_str.split(" "):
        header_bytes.append(int(byte).to_bytes(1, byteorder="little"))
    commands.handle_command(request.form["command"], header_bytes)
    return request.form["command"]

@app.route("/partials/<name>")
def get_partial(name):
    return render_template(name)

if __name__ == "__main__":
    app.run()
