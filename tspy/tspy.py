import sqlite3
from flask import Flask, render_template, jsonify
from flask.ext.triangle import Triangle
from flask.ext.sqlalchemy import SQLAlchemy
from contextlib import closing
import config
import json

app = Flask(__name__)
app.config.from_object(config)
Triangle(app)
db = SQLAlchemy(app)

from models import Message

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    return sqlite3.connect(app.config["DATABASE"])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/messages", methods=["GET"])
def get_messages():
	return json.dumps([
		{
			"age": 13,
			"id": "asdasd",
			"name": "wadwad"
		},
		{
			"age": 13,
			"id": "ASDASDASD",
			"name": "AWSDAWD"
		}
	])

@app.route("/partials/<name>")
def get_partial(name):
	return render_template(name)

if __name__ == "__main__":
    app.run()
