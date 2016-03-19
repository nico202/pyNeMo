#!/usr/bin/env python2

# A worker. Waits for incoming connection on port 10666
# When data are received, process them, and sends back to host (using requests), port 10665

import web #Listen for requests
import requests #Answer to requests when data are processed
import json #Send data
from uuid import getnode as get_mac #Identify machine, debugging purpose

#This will be removed, all these part should be managed by HistoryGUI
from multiprocessing import cpu_count

urls = (
    '/', 'index'
    , '/cores', 'cores'
    
)

class cores:
    def GET(self):
        return json.dumps({"cores": cpu_count()})

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
        
def get_self_ip():
    import socket
    return socket.gethostbyname(socket.gethostname())

port = 10666
mac = str(get_mac())

if __name__ == "__main__":
    app = Worker(urls, globals())
    print("Waiting host connection on: %s:%s"
          %
          (get_self_ip(), port))
    app.run(port)
