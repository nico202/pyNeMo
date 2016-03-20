#!/usr/bin/env python2

'''Shared function for WorkMaster and WorkInit'''


def ip_port(ip, port):
    return "http://"+str(ip)+":"+str(port)

def get_self_ip():
    import socket
    return socket.gethostbyname(socket.gethostname())

#The lisp way, missing macros now
def work_append(ip, data):
    work_manage(ip, "append", data)

def work_start(ip):
    work_manage(ip, "start")
    
def work_manage(ip, action, data = {"msg": True}):
    global client_port
    #Will enable a stop?
    requests.post(ip_port(ip, client_port) + "/" + action, data)
    #TODO: add success/fail codes
