# TSpy #

**This project was only created as a proof of concept, please do not abuse it.**

*This repository was moved from bitbucket to github so the older commits show the wrong username.*

## What? ##

TSpy is a program for hooking into the TeamSpeak 3 server executable. It allows the server owner to read and modify private messages and pokes by setting a breakpoint using GDB at the address where the TeamSpeaks command packets are decrypted and then reading/modifying the packet data.

In addition to reading the messages it is also possible to replace a command message with another command message of desire allowing us to simulate commands. For example if we get a `sendtextmessage` command packet that contains the data `REPLACE` we could then replace this command packet with `clientpoke` to send a poke. In addition to changing the command we can also change from who to whom the message is sent, allowing us to send messages in the name of other users.

TSpy provides a web interface written in Flask and AngularJS that allows viewing captured messages and allows setting up command packets to replace marked packets with.

## Why? ##

I wanted to prove that it is realistically possible for a public server to be modified in such a way that it is not safe for its users and that we shouldn't blindly trust these server providers.

## Project structure ##

All the code related to the interaction with the TeamSpeak server executable is contained in the Python GDB script `tspy_gdb.py`. Everything else is related to either running the server or to the web interface.
