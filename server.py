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
        lines = []
        lines.append("====================================================================\n")
        keys = self.stats.keys()
        for key in keys:
            run_stat = "RUNNING"
            if time.time() - self.stats[key]["time"] > 10:
                run_stat = "STOP"
            lines.append("hostname: {} ({})\n".format(key, run_stat))
            #     "====================================================================\n"
            lines.append("--------------------------------------------------------------------\n")
            gpus = self.stats[key]["gpus"]
            for index in range(len(gpus)):
                gpu = gpus[index]
                lines.append("[{}] | {:3d}% | {:4d}W/{:3}W | {}C | {:5d}MB/{:5d}MB | {}\n".format(
                    index,
                    gpu["utilization.gpu"],
                    gpu["power.draw"],
                    gpu["enforced.power.limit"],
                    gpu["temperature.gpu"],
                    gpu["memory.used"],
                    gpu["memory.total"],
                    gpu["name"]
                ))
            lines.append("====================================================================\n")
        if len(keys) == 0:
            print("====================================================================\n")

        print(''.join(lines))

        with open("stat.txt", "w") as f:
            f.writelines(lines)

    def write_html(self):
        html = ""
        html += "<table>"
        keys = self.stats.keys()
        for key in keys:
            run_stat = "RUNNING"
            if time.time() - self.stats[key]["time"] > 10:
                run_stat = "STOP"
            html += "<tr class='" + run_stat + "'>"
            html += "<td colspan='6'>hostname: {} ({})</td>".format(key, run_stat)
            html += "</tr>"

            gpus = self.stats[key]["gpus"]
            for index in range(len(gpus)):
                gpu = gpus[index]
                html += "<tr class='" + run_stat + "'>"
                html += "<td>[{}]</td> <td>{:3d}%</td> <td>{:4d}W/{:3}W</td> <td>{}C</td> <td>{:5d}MB/{:5d}MB</td> <td>{}</td>\n".format(
                    index,
                    gpu["utilization.gpu"],
                    gpu["power.draw"],
                    gpu["enforced.power.limit"],
                    gpu["temperature.gpu"],
                    gpu["memory.used"],
                    gpu["memory.total"],
                    gpu["name"]
                )
                html += "</tr>"
        if len(keys) == 0:
            print("====================================================================\n")

        html += "</table>"
        with open("stat.html", "w") as f:
            f.writelines(html)


if __name__ == "__main__":

    server = TransServer()
    server.setup()

    os.system("clear")
    while True:
        try:
            server.print_stat()
            server.write_html()
            time.sleep(1)
            os.system("clear")
        except KeyboardInterrupt:
            print("exit")
            exit(0)

