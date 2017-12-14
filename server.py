import json
import argparse
import zmq
import threading
import time
import os

class TransServer:

    def setup(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.bind('tcp://*:5558')
        print('started server')
        self.stats = {}

        self.thread = threading.Thread(target=self.run)
        self.thread.setDaemon(True)
        self.thread.start()

    def run(self):
        while True:
            self.handle()

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.socket.recv()
        dict_stat = json.loads(self.data)
        hostname = dict_stat['hostname']
        dict_stat["time"] = time.time()
        self.stats[hostname] = dict_stat

    def print_stat(self):
        print("======================================================")
        keys = self.stats.keys()
        for key in keys:
            if time.time() - self.stats[key]["time"] > 10:
                del self.stats[key]
            else:
                print("hostname: {}".format(key))
                print("------------------------------------------------------")
                gpus = self.stats[key]["gpus"]
                for index in range(len(gpus)):
                    gpu = gpus[index]
                    print("[{}] name: {}".format(index, gpu["name"]))
                    print("memory: {:5d}/{:5d} | used:{:3d}% | power:{:4d}W/{:3}W | temp: {}C".format(
                        gpu["name"],
                        gpu["memory.used"],
                        gpu["memory.total"],
                        gpu["utilization.gpu"],
                        gpu["power.draw"],
                        gpu["enforced.power.limit"],
                        gpu["temperature.gpu"]
                ))
                print("======================================================")
        if len(keys) == 0:
            print("======================================================")


if __name__ == "__main__":

    server = TransServer()
    server.setup()

    os.system("clear")
    while True:
        try:
            server.print_stat()
            time.sleep(1)
            os.system("clear")
        except KeyboardInterrupt:
            print("exit")
            exit(0)

