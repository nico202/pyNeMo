#!/usr/bin/env python2

'''Shared function for WorkMaster and WorkInit'''

def ip_port(ip, port):
    return "http://"+str(ip)+":"+str(port)

def get_self_ip():
    import socket
    return socket.gethostbyname(socket.gethostname())

#The lisp way, missing macros now
def work_append(ip, port, data):
    if ip == get_self_ip():
        local_work_manage("append", data)
    else:
        work_manage(ip, port, "append", data)

def work_start(ip, port):
    if ip == get_self_ip():
        local_work_manage("start")
    else:
        work_manage(ip, port, "start")


def work_init(ip, port):
    if ip == get_self_ip():
        local_work_manage("init")
    else:
        work_manage(ip, port, "init")
    
def work_manage(ip, client_port, action, data = {"msg": True}):
    import requests
    #Will enable a stop?
    requests.post(ip_port(ip, client_port) + "/" + action, data)
    #TODO: add success/fail codes

def local_work_manage(action, data = True):
    from multiprocessing import cpu_count
    if action == "append":
	return        
    
def response_request(to_save, master_ip, master_port):
    import requests
    requests.post(ip_port(str(master_ip), str(master_port)) + "/save", data = to_save)
    cprint("Result sended, waiting for next", 'okgreen')
