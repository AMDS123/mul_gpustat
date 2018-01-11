import json
import argparse
import zmq
import time
import socket
import requests

def get_hostname():
    hostname = socket.gethostname()
    return hostname

def get_remote_ip():
    ip = ''
    try:
        url = r'http://1212.ip138.com/ic.asp'
        r = requests.get(url)
        txt = r.text
        ip = txt[txt.find("[") + 1: txt.find("]")]
    except:
        print('ip get error')
    return ip


def get_local_ip(opt):
    ip = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((opt.connect_ip, 80))
        ip = s.getsockname()[0]
    except:
        print('ip get error')
    finally:
        s.close()
    return ip


def get_stat_json(opt):
    output = {}
    output['hostname'] = get_hostname()
    output['query_time'] = time.time()
    if opt.get_remote_ip == 1:
        output['remote_ip'] = get_remote_ip()
    output['local_ip'] = get_local_ip(opt)
    return json.dumps(output)

class TransClient:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.setsockopt(zmq.IPV6, 1)

    def start(self, host = 'localhost', port = 5559):
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
    parser.add_argument('--port', type=int, default=5559,
                    help='port')
    parser.add_argument('--socket_timeout', type=int, default=1,
                        help='socket timeout')
    parser.add_argument('--get_remote_ip', type=int, default=0,
                        help='get_remote_ip')
    parser.add_argument('--connect_ip', type=str, default="10.3.9.4",
                        help='connect_ip')
    return parser.parse_args()

if __name__ == "__main__":

    opt = parse_opt()

    socket.setdefaulttimeout(opt.socket_timeout)

    client = TransClient()
    client.start(opt.host, opt.port)

    while True:
        try:
            stat = get_stat_json(opt)
            print(stat)
            client.send(stat)
            time.sleep(1)
        except KeyboardInterrupt:
            print("exit")
            exit(0)