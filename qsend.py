#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import logging
import argparse
import subprocess
import time
import socket

__author__ = "Lu-Chi"

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('<%(asctime)s> <%(levelname)s> : %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class QSendString(object):
    ''''class to prepare and send the string to remote host '''

    def __init__(self, name, uname, comm, esd, ip, port):
        ''' conctructor - initial data out of the user arguments '''

        self.name = name
        self.uname = uname
        self.comm = comm
        self.esd = esd
        self.ip = ip
        self.port = port
        self.datime = time.strftime("%b %d %H:%M:%S")


    def setString(self):
        ''' prepare the string based on initial arguments '''

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
        ''' send prepared string towards dedicated host via netcat '''

        self.cmd = u"echo \"{}\" | nc {} {} -vvvv".format(self.setString(), self.ip, self.port)
        logger.info("[*] Calling the shell.")
        try:
            subprocess.call(self.cmd, shell=True)
        except:
            logger.info("[!] The connection couldn't be established.")
            sys.exit()


    def sendRawSocketData(self):
        ''' send the message using raw socket '''

        logger.info("[*] Creating a socket...")

        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            logger.info("[!] Failed to create socket.")
            sys.exit()

        logger.info("[+] Socket created.")
        logger.info("[*] Connecting host: [{}:{}]".format(self.ip, self.port))

        try:
            self.remote = socket.gethostbyname(self.ip)
            self.s.connect((self.ip, self.port))
        except socket.gaierror:
            logger.info("[!] Hostname could not be resolved. Exiting...")
            sys.exit()

        logger.info("[+] Connection to [{}:{}] established.".format(self.ip, self.port))
        logger.info("[*] Sending a message...")

        try:
            self.s.send(self.setString().encode('utf-8'))
            logger.info("[+] Message sent successfully")
        except socket.error:
            logger.info("[!] Message coud not be sent: {}".format(socket.error))
            self.s.close()
            sys.exit()

        self.s.close()





# main function

def main():


    ip = "10.207.7.10"
    port = 514
    usr = os.getlogin()

    logger.info("[*] Getting user arguments.")

    parser = argparse.ArgumentParser(description="Send syslog message to the remote server.")

    parser.add_argument('-n', '--name', help="the log message", action='store', required=True)
    parser.add_argument('-c','--comment', help="a comment of at least 15 characters", action='store', required=True, type=str)
    parser.add_argument('-e','--esd',help="an ESD ticket number", action='store', required=True, type=int)
    parser.add_argument('-H', '--host', help="host ip", action='store', default=ip, required=False, type=str)
    parser.add_argument('-p','--port', help="host port number", action='store', default=port, required=False, type=str)
    parser.add_argument('-v', '--version', action='store', required=False)

    args = parser.parse_args()

    logger.info("[*] Initializing the object instance.")
    qstr = QSendString(args.name, usr, args.comment, args.esd, args.host, args.port)

    logger.info("[*] Sending the string.")
    #qstr.sendString()
    qstr.sendRawSocketData()



# check if module

if __name__ == '__main__':
    main()



# some necessary stuff to consider
# xc2a6 delimit char = "¦"
# os.getlogin()
# qsend.py -n "some name" -c "Any comment" -e 12345
