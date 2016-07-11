#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import logging
import argparse
import subprocess
import time
import socket


# -------------------
# TODOs:
# -----
# import ConfigParser       - move all ardcodings into the separate ini/xml/csv file
# import pprint             - for better term coloring/presentation
# import re                 - for regexp, testing user arguments
# import setuptools         - for build/install purposes
# import pdb                - just in case any debug stuff needed
# import threading          \
# import multiprocessing     > yep... would be nice... one day... and asyncio
# import Qeueue             /
# -------------------


__author__ = "Lu-Chi"
__copyright__ = "Copyright (C) 2016 Lu-Chi"
__license__ = "Public Domain"
__version__ = "1.0 RC1"



logging.basicConfig(
    filename='qradar_syslog_msg.log',
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    dateftm='%H:%M:%S'
)


console = logging.getLogger("qsend")
console.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('<%(asctime)s> <%(levelname)s> : %(message)s')
ch.setFormatter(formatter)
console.addHandler(ch)


# a class overload for logging module
# class setLogger(logging):
#    pass


# stdlib ConfigParser overload
# class getConfig(ConfigParser):
 #   pass


class QSendString(object):
    """
    class to prepare and send the string to remote host
    """

    def __init__(self, name, uname, comm, esd, ip, port):
        """
        constructor - initial data out of the user arguments
        """

        self.name = name
        self.uname = uname
        self.comm = comm
        self.esd = esd
        self.ip = ip
        self.port = port
        self.datime = time.strftime("%b %d %H:%M:%S")


    def setString(self):
        """
        prepare the string based on initial arguments
        """

        self.pstr = "{} someUniqueSyslogHost\n".format(self.datime)
        self.pstr += "LEEF:2.0|"
        self.pstr += "Euroclear|"
        self.pstr += "RefSetChanger|"
        self.pstr += "v0.1|"
        self.pstr += "DelFromRefSet{}|".format(self.name)
        self.pstr += "xc2a6|"
        self.pstr += u"usrName={}¦".format(self.uname)
        self.pstr += u"value=valueToAdd¦"
        self.pstr += u"comment={}¦".format(self.comm)
        self.pstr += "esdticket={}".format(self.esd)
        self.pstr += "\n"
        return self.pstr


    def sendString(self):
        """
        send prepared string towards dedicated host via netcat
        """

        self.cmd = u"echo \"{}\" | nc {} {} -vvvv".format(self.setString(), self.ip, self.port)
        console.info("Calling the shell.")
        try:
            subprocess.call(self.cmd, shell=True)
        except:
            console.error("The connection couldn't be established.")
            sys.exit()


    def sendRawSocketData(self):
        """
        send the message using raw socket
        """

        console.info("Creating a socket...")

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            console.error("Failed to create a socket.")
            sys.exit()

        console.info("Socket created.")
        console.info("Connecting to: [{}:{}]...".format(self.ip, self.port))

        try:
            self.remote = socket.gethostbyname(self.ip) # watta' matta'... do I really need this sh..t here?
            self.s.connect((self.ip, self.port))
        except socket.error:
            console.error("Connection could not be established. Exiting.")
            sys.exit()

        console.info("Connection to: [{}:{}] established.".format(self.ip, self.port))
        console.info("Sending a message...")

        try:
            self.s.send(self.setString().encode('utf-8'))
            console.info("Message sent successfully.")
        except socket.error:
            console.error("Message coud not be sent: {}.")
            self.s.close()
            sys.exit()

        self.s.close()
        console.info("Socket closed.")
        # so many tries & no throws or raise? hmm... Interesting...



# main function
# sorry guys, it's just a C beneath the remains...

def main():

    # yeah, hardcoded stuff. Better than nothing...
    # oh, wait - what'bout ini?

    ip = "127.0.0.1"
    port = 8000
    usr = os.getlogin()

    console.info("Getting user arguments.")

    parser = argparse.ArgumentParser(description="Send syslog message to the remote server.")

    parser.add_argument('-n', '--name', help="the log message", action='store', required=True, type=str)
    parser.add_argument('-c','--comment', help="a comment of at least 15 characters", action='store', required=True, type=str)
    parser.add_argument('-e','--esd',help="an ESD ticket number", action='store', required=True, type=int)
    parser.add_argument('-H', '--host', help="host ip", action='store', default=ip, required=False, type=str)
    parser.add_argument('-p','--port', help="host port number", action='store', default=port, required=False, type=int)
    parser.add_argument('-v', '--version', action='version', version="[%(prog)s] - Send a syslog message to the remote server - version 1.0 RC1")

    args = parser.parse_args()

    console.info("Initializing the object instance.")
    qstr = QSendString(args.name, usr, args.comment, args.esd, args.host, args.port)
    qstr.sendRawSocketData()



# check if module
# is it? really?

if __name__ == '__main__':
    main()



# some necessary stuff to consider
# --------------------------------
# xc2a6 delimit char = "¦" - freaki' hell with utf-8. Keep in mind the top under shebang.
# os.getlogin()
# qsend.py -n "some name" -c "Any comment" -e 12345
