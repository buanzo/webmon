#!/usr/bin/env python3
# Tool that manages Executor instances switchboard
#

import sys
import zmq
import json
import time
import uuid
from storage import Storage
from pprint import pprint


class ExecutorManager():
    def __init__(self):
        self.zmq_url = "tcp://dispatcher:5559"
        self.connect()

    def connect(self):
        self.zmqCtx = zmq.Context()
        self.zmqSocket = self.zmqCtx.socket(zmq.PUSH)
        self.zmqSocket.connect(self.zmq_url)

    def send_data(self, data=None):
        if data is None:
            return(False)
        ret = self.zmqSocket.send_json(data)
        return(ret)

    def disconnect(self):
        self.zmqSocket.disconnect(self.zmq_url)

    def get_workers(self):  # TODO: use a redis key of some type
        pass

    def get_worker_count(self, score=None):
        ret = Storage.get_worker_count(score=score)
        return(ret)

    def send_pings(self):
        # send pings, one per Name in WORKER_PING_SCORE
        # increment score for NAME in WORKER_PING_SCORE
        data = {}
        data['action'] = 'ping'
        worker_status = Storage.get_worker_status()
        n = len(worker_status[1])
        #print("Manager: Sending {} pings".format(n))
        for x in worker_status[1]:
            name = x[0]
            score = x[1]
            data['name'] = name
            #print("Manager: Pinging {} SCORE={}".format(name, score))
            Storage.worker_increment_score(name=name)
            self.send_data(data=data)

    def get_latest_datestring(self):
        return(Storage.get_latest_datestring())

    def purge_workers(self):
        ret = Storage.worker_purge()
        return(ret)

    def loop(self):
        while True:
            # Step 1, get length of WORKER_NAMES
            #         if > 0, send pings, one per WORKER_NAMES
            #         each ping increments the score for that worker
            #         on WORKER_PING_SCORE key
            # Step 2, check WORKER_PING_SCORES, remove those with score > 30
            #         from WORKER_NAMES and from WORKER_PING_SCORE
            # Step 3, sleep for a second, go back to step 1

            # TODO: add redis database cleanup here? or a daily cron?
            #print("\033[H\033[2J")
            n = self.get_worker_count(score=5)
            print("Manager: There are {} workers with score <= 5.".format(n))
            lds = self.get_latest_datestring()  # TODO: implement
            # print("Latest Datestring: {}".format(lds))
            self.send_pings()
            self.purge_workers()
            time.sleep(1)


if __name__ == '__main__':
    try:
        while True:
            exMgr = ExecutorManager()
            exMgr.loop()
            print("Manager: loop() exited. Shoult not happen.")
            print("Waiting for five seconds for loop() restart.")
            time.sleep(5)
            print("Restarting...")
    except KeyboardInterrupt:
        print("\nCTRL-C. Exiting...")
        sys.exit(0)
