#!/usr/bin/env python2

# The Work-master. Sends data to all the workers via http POST requests
# Listen to answers and saves them to file

import web
web.config.debug = False
import requests
import json
import argparse
import dill
from libs.IO import cprint

from libs.web import ip_port, get_self_ip
from libs.web import work_append, work_start, work_init

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
    , '/', 'stats'
)

class stats:
    '''Accessible through a browser: report % of completition'''
    def GET(self):
        #TODO: add mean loop time, estimated missing, loop/min x slave etc
        global Work
        return "<html>Still missing: "+str(len(Work.queue))+"<br>"\
            "Number of slaves: "+str(len(clients)) + "</html>"

class save:
    def POST(self):
        global Work
        global client_port
        cprint("Data received, saving!", 'okgreen')
        save = open("MultiHeaded-analisys.csv", 'a')
        save.write(web.data())
        save.close()
        cprint("Sending next!", 'okgreen')
        work_append(
            web.ctx['ip'], client_port, Work.pop(1,1))
        work_start(web.ctx['ip'], client_port)
class Worker(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))
    
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
    from time import sleep
    app = Worker(urls, globals())
    info = {}
    #Get info needed as core number etc
    for client in clients:
        info[client] = {}
        success = False
        while not success:
            try:
                response = requests.get(ip_port(client,client_port)+"/cores").text
                success = True
            except requests.exceptions.ConnectionError:
                cprint("Cannot connect to %s" % (client),'fail')
                cprint("Retry in 1 sec", 'info')
                sleep(1)
        info[client]["cores"] = json.loads(response)["cores"]
        info[client]["multiplier"] = json.loads(response)["multiplier"]
    #Add work to queue. Will be started when everyone get it's own
    #(that way we can start the server that receive the results in time)
    #Append a work for every core of every client

    for client_ip in info:
        cprint("Loading data for %s" % client_ip, 'info')
        work_append(
            client_ip, client_port, Work.pop(
                info[client_ip]["cores"]
                , info[client_ip]["multiplier"]))
            
    #Really start the queue
    cprint("Starting all queued",'info')
    for client_ip in info:
        work_init(client_ip, client_port)
        
    #Wait for answers!
    print("Waiting replys on: %s:%s"
          %
          (get_self_ip(), port))
    app.run(port)

