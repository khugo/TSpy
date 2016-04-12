from tspy import db
from datetime import datetime
import json
from sqlalchemy.ext.declarative import DeclarativeMeta

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields
        return json.JSONEncoder.default(self, obj)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    targetmode = db.Column(db.Integer)
    target = db.Column(db.Integer, nullable=True)
    sender = db.Column(db.Integer)
    msg = db.Column(db.String(1025))
    date = db.Column(db.DateTime)

    def __init__(self, sender, msg, targetmode, target=None):
        self.sender = sender
        self.msg = msg
        self.targetmode = targetmode
        self.target = target
        self.date = datetime.now()

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d["date"] = d["date"].strftime("%Y-%m-%d %H:%M:%S")
        return d

class QueuedCommand(db.Model):
    __tablename__ = "queued_commands"
    id = db.Column(db.Integer, primary_key=True)
    #Header contains 13 hex bytes in format:
    #"D3 A1 09 11 FF 66 ?? ?? ?? A1 D6 F1 B3"
    #?? = byte should be copied from the original packet
    header = db.Column(db.String(38))
    command = db.Column(db.String(1025))
    extra = db.Column(db.String(1000))
    completed = db.Column(db.Boolean())

    def __init__ (self, command, header="", extra=""):
        self.command = command
        self.extra = extra
        if header == "":
            self.header = " ".join(["??" for x in range(0, 13)])
        else:
            self.header = header
        self.completed = False

    def as_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return d