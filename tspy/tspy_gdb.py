import gdb
import re
import threading
import json
import traceback
from urllib.request import urlopen
from urllib.parse import urlencode

DECRYPTED_PACKETS_BREAKPOINT = "*0x08238C2D"
CONFIG_PATH = "../tspy_config.json"

def to_uint(x):
    return x & 0xffffffff

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.loads(f.read())

class TSpyBreakpoint(gdb.Breakpoint):
    """
        Ask the server what we should replace the special packet with.
        Returns a json structure:
        {
            command: String,
            header: String, # eg. ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 00 01 23, ?? means that we should use the byte in the real header
            extra: String # if any extra data is needed, it is provided here in a JSON string
        }

    """
    def get_action_from_server(self):
        url = "http://localhost:5000/api/queue?secret=" + self.config["password"]
        json_data = json.loads(urlopen(url).read().decode("utf-8"))
        print(json.dumps(json_data))
        return json_data

    """
        Overwrites the memory according to command_data.
    """
    def apply_server_action(self, command_data):
        self.set_command(command_data["command"])
        self.set_size(len(command_data["command"])+13)
        for index, hex_byte in enumerate(command_data["header"].split(" ")):
            #If byte is set to ?? we keep the original one
            if hex_byte != "??":
                value = int(hex_byte, 16)
                self.inferior.write_memory(self.data_addr + index, bytes((value,)))

    def read_command(self):
        size = int.from_bytes(self.inferior.read_memory(self.data_size_addr, 4), "little") - 13
        memory = self.inferior.read_memory(self.data_addr+13, size)
        command = ""
        for b in memory:
            try:
                command += b.decode("utf-8")
            except UnicodeDecodeError:
                byte = hex(int.from_bytes(b, "little"))
                command += byte #add as raw hex encoded byte
                print("Failed to decode " + byte)

        return command
    def read_size(self):
        return int.from_bytes(self.inferior.read_memory(self.data_size_addr, 4), "little") - 13
    def print_header(self):
        output = ""
        for b in self.inferior.read_memory(self.data_addr, 13):
            output += str(hex(int.from_bytes(b, "little"))) + " "
        print(output)
    def header_to_packet(self):
        output = ""
        for b in self.inferior.read_memory(self.data_addr, 13):
            output += str(hex(int.from_bytes(b, "little"))).replace("0x", "") + " "
        return output.strip()
    def set_clid(self, clid):
        self.inferior.write_memory(self.data_addr + 11, bytes((clid,)))
    def set_packet_type(self, packet_type):
        self.inferior.write_memory(self.data_addr + 12, bytes((packet_type,)))
    def set_command(self, command):
        self.inferior.write_memory(self.data_addr + 13, command.encode("utf-8"))
    def set_size(self, size):
        self.inferior.write_memory(self.data_size_addr, bytes((size,)))
    def log_packet(self, command):
        output = header_to_packet() + "\t" + command
        with open(self.config["packet_logs_path"], "a+") as f:
            f.write(output)
            f.write("\n\n")

    """
        Entry point.
    """
    def stop(self):
        try:
            self.config = load_config()
            self.inferior = gdb.selected_inferior()
            data_ptr_addr = to_uint(int(gdb.parse_and_eval("$esi+4")))
            #data_addr + 13 = start of command message
            self.data_addr = int.from_bytes(self.inferior.read_memory(data_ptr_addr, 4), "little")
            self.data_size_addr = to_uint(int(gdb.parse_and_eval("$esi+8")))
            if self.read_size() > 0:
                command = self.read_command()
                if command.startswith("sendtextmessage"):
                    msg = re.search("msg=(.*)", command)
                    print(command)
                    if not msg:
                        raise Exception("Couldn't find msg in sendtextmessage: " + command)
                    #If this is a special packet, get what the server wants to do and replace memory accordingly
                    if msg.group(1) == self.config["trigger_packet_content"]:
                        server_action = self.get_action_from_server()
                        if server_action["command"] != "":
                            self.apply_server_action(server_action)
                            self.print_header()
                    #Utility for debugging, writes invokers client id to channel chat.
                    elif msg.group(1) == "clid":
                        new_command = "sendtextmessage targetmode=2 msg=" + str(int.from_bytes(self.inferior.read_memory(self.data_addr+11, 1), "little"))
                        self.set_command(new_command)
                        self.set_size(len(new_command)+13)
                if self.config["log_packets"]:
                    self.log_packet(command)
                data = urlencode({"command":command, "header":self.header_to_packet()}).encode("utf-8")
                urlopen("http://localhost:5000/api/report/command?secret=" + self.config["password"], data)
        except Exception as e:
            traceback.print_exc()
            data = urlencode({"error_msg": str(e), "exception": type(e).__name__, "traceback": traceback.format_exc()}).encode("utf-8")
            try:
                urlopen("http://localhost:5000/api/report/error?secret=" + self.config["password"], data)
            except Exception as e:
                print("Got Exception while trying to report error to server.")
                traceback.print_exc()

class TSpy(gdb.Command):
    def __init__(self):
        super (TSpy, self).__init__("ow", gdb.COMMAND_USER)
    def invoke (self, arg, from_tty):
        TSpyBreakpoint(DECRYPTED_PACKETS_BREAKPOINT)
        print("""
        ******************************************
        *            TSpy Activated!             *
        *                                        *
        ******************************************
        """)
        print("Overwriting commands at " + DECRYPTED_PACKETS_BREAKPOINT)

TSpy()
