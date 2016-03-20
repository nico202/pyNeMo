#!/usr/bin/env python2

# A worker. Waits for incoming connection on port 10666
# When data are received, process them, and sends back to host (using requests), port 10665

import web #Listen for requests
web.config.debug = False

import requests #Answer to requests when data are processed
import json #Send data
import dill
from uuid import getnode as get_mac #Identify machine, debugging purpose

#This will be removed, all these part should be managed by HistoryExplorer
from multiprocessing import cpu_count
from HistoryExplorer import dispatch_jobs

web.config.debug = False
urls = (
    '/', 'index'
    , '/cores', 'cores' #Return number of available cores (add --cores cli)
    , '/append', 'append' #Append a work to the queue
    , '/start', 'start' #Start all works in the queue
)

master_ip = ""
class cores:
    def GET(self):
        import config
        global master_ip
        master_ip = web.ctx["ip"]
        multiplier = 1 if not hasattr(config, 'MULTIPLIER') else config.MULTIPLIER        
        return json.dumps(
            {
                "cores": cpu_count()
                , "multiplier": multiplier})

#FIXME: shared beetween 2 script
def ip_port(ip, port):
    return "http://"+str(ip)+":"+str(port)

class workQueue:
    def __init__(self):
        self.workqueue = []
    def append(self, data):
        workqueue = data

class append:
    def POST(self):
        global Work
        import dill
        loaded = dill.loads(web.data())
        Work.workqueue = loaded
        return True #Allow error codes

class start: #Maybe should be a GET?
    def POST(self):
        global Work
        global master_ip
        outputs = []
        titles = []
        for work_id in Work.workqueue:
            outputs.append(Work.workqueue[work_id]["data"])
            titles.append(Work.workqueue[work_id]["title"])
        #check if we are really remote or same machine
        dispatch_jobs(titles, cpu_count(), remote = master_ip, in_data = outputs)

        return True

class index:
    def GET(self):
        return "Hello, world!"
    def POST(self): #Input: {filename: raw_compressed_data}
        print(web.input())
        return {mac: "starting"}

class Worker(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))
    
class RequestHandler():
    def POST():
        data = web.data() # you can get data use this method

#FIXME: shared between 2 script
def get_self_ip():
    import socket
    return socket.gethostbyname(socket.gethostname())

port = 10666
mac = str(get_mac())

Work = workQueue()
if __name__ == "__main__":
    app = Worker(urls, globals())
    
    print("Waiting host connection on: %s:%s"
          %
          (get_self_ip(), port))
    app.run(port)
