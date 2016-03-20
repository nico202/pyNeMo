#!/usr/bin/env python2

'''Shared function for WorkMaster and WorkInit'''

def ip_port(ip, port):
    return "http://"+str(ip)+":"+str(port)

def get_self_ip():
    import socket
    return socket.gethostbyname(socket.gethostname())

#The lisp way, missing macros now
def work_append(ip, port, data):
    work_manage(ip, port, "append", data)

def work_start(ip, port):
    work_manage(ip, port, "start")

def work_init(ip, port):
    work_manage(ip, port, "init")
    
def work_manage(ip, client_port, action, data = {"msg": True}):
    import requests
    #Will enable a stop?
    requests.post(ip_port(ip, client_port) + "/" + action, data)
    #TODO: add success/fail codes
