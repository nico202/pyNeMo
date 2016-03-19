#!/usr/bin/env python2

# The Work-master. Sends data to all the workers via http POST requests
# Listen to answers and saves them to file

import web
import requests
import json
import argparse

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

args = parser.parse_args()

clients = args.ip_list

urls = (
    '/', 'index'
)

class index:
    def GET(self):
        return "Hello, world!"
    def POST(self): #Input: {filename: raw_compressed_data}
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

port = 10665
client_port = 10666
ip = get_self_ip()
if __name__ == "__main__":
    app = Worker(urls, globals())
    info = {}
    for client in clients:
        info[client] = {}
        response = requests.get("http://"+client+":"+str(client_port)+"/cores").text
        info[client]["cores"] = json.loads(response)["cores"]
    print info
    print("Waiting replys on: %s:%s"
          %
          (get_self_ip(), port))
    app.run(port)

