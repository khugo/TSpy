from tspy import db

class Message(db.Model):
	__tablename__ = "messages"

	id = db.Column(db.Integer, primary_key=True)
	sender = db.Column(db.String())
	msg = db.Column(db.String())

	def __init__(self, sender, msg):
		self.sender = sender
		self.msg = msg

	def __repr__(self):
		return "<id {}>".format(self.id)