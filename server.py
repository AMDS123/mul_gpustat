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

        self.thread_ip = threading.Thread(target=self.write_ip)
        self.thread_ip.setDaemon(True)
        self.thread_ip.start()

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

            local_ip = ""
            remote_ip = ""
            if 'local_ip' in self.stats[key]:
                local_ip = "[" + self.stats[key]["local_ip"] + "]"
            if 'remote_ip' in self.stats[key]:
                remote_ip = "[" + self.stats[key]["remote_ip"] + "]"

            lines.append("{} ({}) {} {}\n".format(key, run_stat, local_ip, remote_ip))
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
            if time.time() - self.stats[key]["time"] > 5:
                run_stat = "STOP"

            local_ip = ""
            remote_ip = ""
            if 'local_ip' in self.stats[key]:
                local_ip = "[" + self.stats[key]["local_ip"] + "]"
            if 'remote_ip' in self.stats[key]:
                remote_ip = "[" + self.stats[key]["remote_ip"] + "]"

            html += "<tr class='" + run_stat + "'>"
            html += "<td colspan='7'>{} ({}) {} {}</td>".format(key, run_stat, local_ip, remote_ip)
            html += "</tr>"

            gpus = self.stats[key]["gpus"]
            for index in range(len(gpus)):
                run_stat1 = run_stat
                gpu = gpus[index]
                if run_stat1 != "STOP" and gpu["utilization.gpu"] < 5:
                    run_stat1 = "IDEL"
                html += "<tr class='" + run_stat1 + "'>"
                html += "<td>[{}]</td> <td width='45px'>{:3d}%</td> <td>{:4d}W/{:3}W</td> <td>{}C</td> <td>{:5d}MB/{:5d}MB</td> <td>{}</td><td>{}</td>\n".format(
                    index,
                    gpu["utilization.gpu"],
                    gpu["power.draw"],
                    gpu["enforced.power.limit"],
                    gpu["temperature.gpu"],
                    gpu["memory.used"],
                    gpu["memory.total"],
                    gpu["name"],
		    '|'.join(['{}({}M)'.format(_['username'],_['gpu_memory_usage']) for _ in gpu["processes"]])
                )
                html += "</tr>"
        if len(keys) == 0:
            print("====================================================================\n")

        html += "</table>"
        with open("stat.html", "w") as f:
            f.writelines(html)

    def write_ip(self):
        while True:
            keys = self.stats.keys()
            for key in keys:
                if 'remote_ip' in self.stats[key]:
                    remote_ip = self.stats[key]["remote_ip"]
                    with open(key + "_ip.txt", "w") as f:
                        f.write(remote_ip)

            time.sleep(1)


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

