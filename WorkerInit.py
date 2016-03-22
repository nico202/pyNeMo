#!/usr/bin/env python2

# A worker. Waits for incoming connection on port 10666
# When data are received, process them, and sends back to host (using requests), port 10665

import web #Listen for requests
from libs.web import ip_port, get_self_ip

web.config.debug = False

import requests #Answer to requests when data are processed
import json #Send data
import dill
from uuid import getnode as get_mac #Identify machine, debugging purpose

#This will be removed, all these part should be managed by HistoryExplorer
from multiprocessing import cpu_count
from HistoryExplorer import main_loop
from libs.multiProcess import dispatch_jobs

web.config.debug = False
urls = (
    '/', 'index'
    , '/cores', 'cores' #Return number of available cores (add --cores cli)
    , '/append', 'append' #Append a work to the queue
    , '/init', 'init' #Start all works in the queue
    , '/start', 'start' #Start newly appended
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


class workQueue:
    def __init__(self):
        self.workqueue = []
    def append(self, data):
        self.workqueue.append(data)
    def pop(self):
        try:
            ret = self.workqueue.pop()
        except IndexError:
            ret = False
        return ret

class append:
    def POST(self):
        global Work
        import dill
        loaded = dill.loads(web.data())
        Work.append(loaded)
        return True #Allow error codes

class start:
    #Start one only
    #It's multiprocessing since web.py provides it, and
    #We are spawning 1 new process as soon as one finish
    def POST(self):
        global titles
        next_work = Work.pop()
        outputs = []; titles = []
        if next_work:
            for i in next_work: #Should be just 1
                outputs.append(next[i]["data"])
                titles.append(next_work[i]["title"])
        main_loop(titles, web.ctx['ip'], outputs)

class init: #Maybe should be a GET?
    #Use multiprocessing implemented by me
    #(thanks to StackO)
    def POST(self):
        global Work
        global master_ip
        cpu_number = cpu_count()
        outputs = []
        titles = []
        for i in range(cpu_number):
            next_work = Work.pop()
            if next_work:
                outputs.append(next_work[i]["data"])
                titles.append(next_work[i]["title"])
        #check if we are really remote or same machine
        dispatch_jobs(titles, cpu_number, remote = master_ip, in_data = outputs)
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

port = 10666
mac = str(get_mac())

Work = workQueue()
if __name__ == "__main__":
    app = Worker(urls, globals())
    
    print("Waiting host connection on: %s:%s"
          %
          (get_self_ip(), port))
    app.run(port)
