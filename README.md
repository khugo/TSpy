# TSpy #

**Only for educational purposes, not meant to do harm.**

TSpy is an application that hooks into the Teamspeak 3 server executable using GDB and is able to read the packets sent to and sent by the server when they are in decrypted state, allowing for example reading all the text messages sent by the clients connected to the server. It is also capable of replacing the packet contents so that for example you can change the recipient or content of the text message. See the `tspy_gdb.py` for the GDB script.

TSpy also has a web interface written in Flask.