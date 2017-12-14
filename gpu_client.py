import gpustat
import json
import argparse
import zmq
import time

def get_gpu_stat_json():
    gpustats = gpustat.GPUStatCollection.new_query()
    output = gpustats.jsonify()
    return json.dumps(output)

class TransClient:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)

    def start(self, host = 'localhost', port = 5558):
        self.host = host
        self.port = port
        server_info = "tcp://" + self.host + ":" + str(self.port)
        self.socket.connect(server_info)
        print("connected to server: " + server_info)

    def close(self):
        self.socket.close()

    def send(self, msg):
        self.socket.send(msg)

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='localhost',
                    help='host')
    parser.add_argument('--port', type=int, default=5558,
                    help='port')
    return parser.parse_args()

if __name__ == "__main__":

    opt = parse_opt()

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