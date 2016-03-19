#!/usr/bin/env python2

# The Work-master. Sends data to all the workers via http POST requests
# Listen to answers and saves them to file

import web
import requests
import json
import argparse
import dill
from libs.Io import cprint
from HistoryExplorer import list_all, read_output


parser = argparse.ArgumentParser(description='Deploy analysis on multiple machines')
parser.add_argument('--history-dir',
                    help = 'Path of the history dir'
                    , dest = 'path'
                    , default = "history"
)
parser.add_argument('--ip-list',
                    help = 'List of ip of systems listening on 10666'
                    , dest = 'ip_list'
                    , default = 0
                    , nargs='+'
                    , type=str
                    
    )
parser.add_argument('--start-from',
                    help = 'Which file (loop) to start with'
                    , dest = 'start_from'
                    , default = 0
)
parser.add_argument('--end-to',
                    help = 'Which file (loop) to end with'
                    , dest = 'end_to'
                    , default = False
)

args = parser.parse_args()
    
clients = args.ip_list

outputs, total = list_all(args.path, args.start_from, args.end_to)

urls = (
    '/save', 'save'
    , '/index', 'stats'
)

class stats:
    '''Accessible through a browser: report % of completition'''
    

class save:
    def POST(self):
        global Work
        cprint("Data received, saving!", 'okgreen')
        save = open("MultiHeaded-analisys.csv", 'a')
        save.write(web.data())
        save.close()
        cprint("Sending next!", 'okgreen')
        work_append(
            web.ctx['ip'], Work.pop(1,1))

class Worker(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))
    
#class RequestHandler():
#    def POST():
#        data = web.data() # you can get data use this method
        
def get_self_ip():
    import socket
    return socket.gethostbyname(socket.gethostname())

def ip_port(ip, port):
    return "http://"+str(ip)+":"+str(port)

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

port = 10665
client_port = 10666
ip = get_self_ip()

class workQueue:
    def __init__(self, (queue, printable_total)):
        self.queue = queue
    def pop(self, cores, multiplier):
        global args
        to_give = {}
        for i in range(int(cores * multiplier)):
            filename = self.queue.pop()
            to_give[i] = {"title":filename,
                          "data": read_output(filename, args.path)}

        return dill.dumps(to_give)

Work = workQueue(list_all(args.path, args.start_from, args.end_to))
if __name__ == "__main__":
    from libs.IO import cprint
    app = Worker(urls, globals())
    info = {}
    #Get info needed as core number etc
    for client in clients:
        info[client] = {}
        response = requests.get(ip_port(client,client_port)+"/cores").text
        info[client]["cores"] = json.loads(response)["cores"]
        info[client]["multiplier"] = json.loads(response)["multiplier"]
    #Add work to queue. Will be started when everyone get it's own
    #(that way we can start the server that receive the results in time)
    #Append a work for every core of every client

    for client_ip in info:
        cprint("Loading data for %s" % client_ip, 'info')
        work_append(
            client_ip, Work.pop(
                info[client_ip]["cores"]
                , info[client_ip]["multiplier"]))
            
    #Really start the queue
    cprint("Starting all queued",'info')
    for client_ip in info:
        work_start(client_ip)
        
    #Wait for answers!
    print("Waiting replys on: %s:%s"
          %
          (get_self_ip(), port))
    app.run(port)

