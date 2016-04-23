import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, send_from_directory
from flask.ext.triangle import Triangle
from flask.ext.sqlalchemy import SQLAlchemy
from contextlib import closing
import config
import json
import os
from functools import wraps

app = Flask(__name__)
app.config.from_object(config)
Triangle(app)
db = SQLAlchemy(app)


import commands
from models import *

def secret_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "secret" in request.args and request.args["secret"] == config.ACCESS_PASSWORD:
            return f(*args, **kwargs)
        else:
            return "", 404
    return decorated_function

@app.route("/")
@secret_required
def index():
    return render_template("base.html", secret=config.ACCESS_PASSWORD)

@app.route("/static/js/<path:filename>")
@secret_required
def javascript_files(filename):
    print(os.path.join(app.root_path, "static/js"))
    return send_from_directory(
        os.path.join(app.root_path, "static/js"),
        filename
    )

@app.route("/api/inspect/messages", methods=["GET"])
@secret_required
def get_messages():
    return json.dumps([x.as_dict() for x in Message.query.order_by("date desc")])

@app.route("/api/inspect/queue", methods=["GET"])
@secret_required
def get_queue():
    return json.dumps([x.as_dict() for x in QueuedCommand.query.filter_by(completed=False).order_by("id")])

@app.route("/api/inspect/queue/completed", methods=["GET"])
@secret_required
def get_completed_queue():
    return json.dumps([x.as_dict() for x in QueuedCommand.query.filter_by(completed=True).order_by("-id").limit(50)])

@app.route("/api/command", methods=["POST"])
@secret_required
def handle_command():
    header_str = request.form["header"]
    print("Got header " + header_str)
    header_bytes = []
    for byte in header_str.split(" "):
        header_bytes.append(int(byte).to_bytes(1, byteorder="little"))
    commands.handle_command(request.form["command"], header_bytes)
    return request.form["command"]

@app.route("/api/queue", methods=["GET"])
@secret_required
def get_next_queued_command():
    command = QueuedCommand.query.filter_by(completed=False).order_by("id").first()
    if command:
        json_obj = json.dumps(command.as_dict())
        command.completed = True
        db.session.commit()
    else:
        json_obj = json.dumps({"command": "", "header": "", "extra": "", "id": -1})
    return json_obj

@app.route("/api/queue", methods=["POST"])
@secret_required
def add_new_queued_command():
    header = ""
    command = ""
    extra = ""
    if "command" in request.form:
        command = request.form["command"]
    else:
        return json.dumps({"error": "command argument was not provided"}), 400
    if "header" in request.form:
        header = request.form["header"]
    if "extra" in request.form:
        extra = request.form["extra"]
    command = QueuedCommand(command=command, header=header, extra=extra)
    db.session.add(command)
    db.session.commit()
    return "OK", 200

@app.route("/api/queue/delete", methods=["POST"])
@secret_required
def delete_queued_command():
    if "id" in request.form:
        id = request.form["id"]
    else:
        return json.dumps({"error": "id argument was not provided"}), 400
    command = QueuedCommand.query.filter_by(id=int(request.form["id"])).first()
    if command:
        db.session.delete(command)
        db.session.commit()
        return "OK", 200
    else:
        return json.dumps({"error": "couldn't find command"}), 404

@app.route("/partials/<name>")
@secret_required
def get_partial(name):
    return render_template(name)

if __name__ == "__main__":
    app.run()
