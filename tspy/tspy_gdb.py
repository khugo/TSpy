import gdb
import re
import threading
import json
from urllib.request import urlopen
from urllib.parse import urlencode

DECRYPTED_PACKETS_BREAKPOINT = "*0x08238C2D"
INBOUND_PACKETS_OUTPUT = "../inbound_packets.txt"
#What the sendtextmessage packet's message should contain for it to be replaced
TRIGGER_PACKET_CONTENT = "tspy"

def to_uint(x):
    return x & 0xffffffff

class DecryptedBreakpoint(gdb.Breakpoint):
    def stop(self):
        inferior = gdb.selected_inferior()
        data_ptr_addr = to_uint(int(gdb.parse_and_eval("$esi+4")))
        size_ptr_addr = to_uint(int(gdb.parse_and_eval("$esi+8")))

        data_size = int.from_bytes(inferior.read_memory(size_ptr_addr, 4), "little")
        data_addr = int.from_bytes(inferior.read_memory(data_ptr_addr, 4), "little")
        if data_size > 0:
            memory = inferior.read_memory(data_addr, data_size)
            output = ""
            for index, b in enumerate(memory):
                if index < 13: #Log header as hex bytes
                    output += str(hex(int.from_bytes(b, "little"))) + " "
                    if index == 12:
                        output += "\t"
                else:  
                    try:
                        output += b.decode("utf-8")
                    except UnicodeDecodeError: #If can't decode append as hex
                        output += str(hex(int.from_bytes(b, "little")))
            if len(output) > 0:
                with open(INBOUND_PACKETS_OUTPUT, "a+") as f:
                    f.write(output)
                    f.write("\n\n")

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
        url = "http://localhost:5000/api/queue"
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
                print("Failed to decode " + str(int.from_bytes(b, "little")))
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
            output += str(int.from_bytes(b, "little")) + " "
        return output.strip()
    def set_clid(self, clid):
        self.inferior.write_memory(self.data_addr + 11, bytes((clid,)))
    def set_packet_type(self, packet_type):
        self.inferior.write_memory(self.data_addr + 12, bytes((packet_type,)))
    def set_command(self, command):
        self.inferior.write_memory(self.data_addr + 13, command.encode("utf-8"))
    def set_size(self, size):
        self.inferior.write_memory(self.data_size_addr, bytes((size,)))

    """
        Entry point.
    """
    def stop(self):
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
                    return
                #If this is a special packet, get what the server wants to do and replace memory accordingly
                if msg.group(1) == TRIGGER_PACKET_CONTENT:
                    server_action = self.get_action_from_server()
                    if server_action["command"] != "":
                        self.apply_server_action(server_action)
                        self.print_header()
                #Utility for debugging, writes invokers client id to channel chat.
                elif msg.group(1) == "clid":
                    new_command = "sendtextmessage targetmode=2 msg=" + str(int.from_bytes(self.inferior.read_memory(self.data_addr+11, 1), "little"))
                    self.set_command(new_command)
                    self.set_size(len(new_command)+13)
                else:
                    data = urlencode({"command":command, "header":self.header_to_packet()}).encode("utf-8")
                    threading.Thread(target=urlopen, args=("http://localhost:5000/api/command", data)).start()

class LogInboundPackets(gdb.Command):
    def __init__ (self):
         super (LogInboundPackets, self).__init__("log_packets", gdb.COMMAND_USER)
    def invoke (self, arg, from_tty):
        DecryptedBreakpoint(DECRYPTED_PACKETS_BREAKPOINT)
        print("Set a breakpoint at " + DECRYPTED_PACKETS_BREAKPOINT)

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

#LogInboundPackets()
TSpy()