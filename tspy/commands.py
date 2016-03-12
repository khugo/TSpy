import re
from tspy import db
from models import *

def parse_header(bytes):
	return {
		"clid": 15
	}
	try:
		header = {
			"clid": int.from_bytes(bytes[11], "little"),
			"packet_type": int.from_bytes(bytes[12], "little")
		}
	except IndexError:
		raise InvalidHeaderError("Header out of range: " + bytes)

def handle_command(command, header_bytes):
	header = parse_header(header_bytes)
	command_name = command[:command.find(" ")]
	if command_name == "sendtextmessage":
		handle_message(command, header)

def handle_message(command, header):
	TARGETMODE_SERVER = 3
	TARGETMODE_CHANNEL = 2
	TARGETMODE_CLIENT = 1
	try:
		targetmode = int(re.search("targetmode=([1-3])", command).groups(1)[0])
		msg = re.search("msg=(.*)", command).groups(1)[0]
		target = None
		if targetmode == TARGETMODE_CLIENT or targetmode == TARGETMODE_CHANNEL:
			target = int(re.search("target=([0-9]+)", command).groups(1)[0])
		sender = header["clid"]
		print(sender, msg, targetmode, target)
		m = Message(sender, msg, targetmode, target)
		db.session.add(m)
		db.session.commit()
	except AttributeError:
		raise InvalidCommandError("Invalid parameters in sendtextmessage: " + command)

class InvalidHeaderError(Exception):
	pass
class InvalidCommandError(Exception):
	pass
