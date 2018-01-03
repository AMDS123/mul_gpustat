import gpustat
import json
import argparse
import zmq
import time
import urllib
import re
import socket

def get_remote_ip():
    ip = ''
    try:
        ipinfo = urllib.urlopen("http://ip.chinaz.com/getip.aspx").read()
        ip = re.findall(r"ip:'(.*?)',", ipinfo)[0]
    except:
        print('ip get error')
    return ip

def get_local_ip():
    ip = ''
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
    except:
        print('ip get error')
    return ip


def get_gpu_stat_json():
    gpustats = gpustat.GPUStatCollection.new_query()
    output = gpustats.jsonify()
    output['query_time'] = time.time()
    output['remote_ip'] = get_remote_ip()
    output['local_ip'] = get_local_ip()
    return json.dumps(output)

class TransClient:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)

    def start(self, host = 'localhost', port = 5558):
        self.host = host
        self.port = port
        self.server_info = "tcp://" + self.host + ":" + str(self.port)
        self.socket.connect(self.server_info)
        print("connected to server: " + self.server_info)

    def reconnect(self):
        self.socket.close()
        self.socket.connect(self.server_info)
        print("reconnected to server: " + self.server_info)

    def close(self):
        self.socket.close()

    def send(self, msg):
        try:
            self.socket.send(msg)
        except:
            self.reconnect()

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='localhost',
                    help='host')
    parser.add_argument('--port', type=int, default=5558,
                    help='port')
    parser.add_argument('--socket_timeout', type=int, default=1,
                        help='port')
    return parser.parse_args()

if __name__ == "__main__":

    opt = parse_opt()

    socket.setdefaulttimeout(opt.socket_timeout)

    client = TransClient()
    client.start(opt.host, opt.port)

    while True:
        try:
            stat = get_gpu_stat_json()
            print(stat)
            client.send(stat)
            time.sleep(1)
        except KeyboardInterrupt:
            print("exit")
            exit(0)