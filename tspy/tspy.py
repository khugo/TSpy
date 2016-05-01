import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, send_from_directory, make_response
from flask.ext.triangle import Triangle
from flask.ext.sqlalchemy import SQLAlchemy
from contextlib import closing
import config
import json
import os
import traceback
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
        #Support both query param (for gdb script) and cookies (browser)
        if "secret" in request.cookies and request.cookies["secret"] == config.ACCESS_PASSWORD:
            return f(*args, **kwargs)
        elif "secret" in request.args and request.args["secret"] == config.ACCESS_PASSWORD:
            return f(*args, **kwargs)
        else:
            return "", 404
    return decorated_function

@app.route("/")
def index():
    #If we have secret in query params set it as cookie and redirect back to this
    if "secret" in request.args and request.args["secret"] == config.ACCESS_PASSWORD:
        response = make_response(redirect("/"))
        response.set_cookie("secret", request.args["secret"])
        return response
    elif "secret" in request.cookies and request.cookies["secret"] == config.ACCESS_PASSWORD:
        return render_template("base.html", secret=config.ACCESS_PASSWORD)
    else:
        return "", 404

@app.route("/static/js/<path:filename>")
@secret_required
def javascript_files(filename):
    return send_from_directory(
        os.path.join(app.root_path, "static/js"),
        filename
    )

@app.route("/api/inspect/messages", methods=["GET"])
@secret_required
def get_messages():
    return json.dumps([x.as_dict() for x in Message.query.order_by("date desc").limit(150)])

@app.route("/api/inspect/errors", methods=["GET"])
@secret_required
def get_errors():
    return json.dumps([x.as_dict() for x in Error.query.order_by("date desc").limit(150)])

@app.route("/api/inspect/queue", methods=["GET"])
@secret_required
def get_queue():
    return json.dumps([x.as_dict() for x in QueuedCommand.query.filter_by(completed=False).order_by("id")])

@app.route("/api/inspect/queue/completed", methods=["GET"])
@secret_required
def get_completed_queue():
    return json.dumps([x.as_dict() for x in QueuedCommand.query.filter_by(completed=True).order_by("-id").limit(150)])

@app.route("/api/report/command", methods=["POST"])
@secret_required
def handle_command():
    try:
        header_str = request.form["header"]
        print("Got command " + request.form["command"])
        print("Got header " + header_str)
        header_bytes = []
        for byte in header_str.split(" "):
            header_bytes.append(int(byte, 16).to_bytes(1, byteorder="little"))
        commands.handle_command(request.form["command"], header_bytes)
    except Exception as e:
        traceback.print_exc()
        return traceback.format_exc(), 500
    return request.form["command"], 200

@app.route("/api/report/error", methods=["POST"])
@secret_required
def handle_error():
    e = Error(error_msg=request.form["error_msg"], exception=request.form["exception"], traceback=request.form["traceback"])
    db.session.add(e)
    db.session.commit()
    return "OK", 200

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
