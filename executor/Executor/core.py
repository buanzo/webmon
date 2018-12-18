#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo 'Buanzo' Busleiman

import os
import sys
import zmq
import uuid
from Executor.storage import Storage

from pathlib import Path
from pprint import pprint

from Executor.plugin import ExecutorPluginBase


class ExecutorCore():
    PLUGIN_HOOKS = ('setup', 'run',)
    VALID_ACTIONS = ('queue_jobs', 'set_name', 'ping')

    def __init__(self):
        self.running_jobs = {}
        self.name = None

    def worker_pong(self):
        while self.name is None:
            name = uuid.uuid4().hex
            if self.set_name(name=name) is not None:
                self.name = name
        msg = "[I] Worker name set to {}".format(self.name)
        Storage.worker_reset_score(name=self.name)

    def set_name(self, name=None):
        if self.name is not None:
            return(None)
        if name is None:
            return(None)
        if Storage.worker_name_taken(name=name):
            print("Name={} already taken".format(name))
            self.name = None
            return(None)
        self.name = name
        ret = Storage.worker_name_set(name=name)
        print("Name={} IS NOW OURS".format(name))
        return(ret)

    def run_plugins(self, workSpec=None):
        if workSpec is None:
            return

        # Run all hooks, in order, on every plugin
        ds = workSpec['datestring']

        if workSpec['action'] in ExecutorCore.VALID_ACTIONS:
            cmd = workSpec['action']
        else:
            cmd = None

        # TODO: separate code by workSpec['action']
        ds = workSpec['datestring']
        nJobs = len(workSpec['data'])
        if nJobs == 0:
            return(None)

        print("Processing {} jobs for date identifier {}".format(nJobs, ds))
        for work in workSpec['data']:
            for hook in ExecutorCore.PLUGIN_HOOKS:
                for plugin in self.plugins:
                    if hasattr(plugin, hook):
                        if hook == 'setup':  # Better than re-initializing
                            getattr(plugin, hook)(datestring=ds,
                                                  workername=self.name,
                                                  cmd=cmd)
                        else:
                            aId = work['asset_id']
                            msg = "Asset ID {} - Running {}:{}()"
                            print(msg.format(aId, plugin.name, hook))
                            getattr(plugin, hook)(work=work)
                            self.worker_pong()  # Jobs take time
        print("Batch complete.\n")

    """ main() is indeed main().
        it gets plugins, and might get more stuff
        TODO: it needs to:
        * collect declarative data off plugins
        * resolve execution and plugin requirements
        * update the ExecutorCore status class attribute
    """
    def main(self, plugins=None):
        print("[*] Initializing plugins")
        self.plugins = [P() for P in plugins]

        print("[*] Contacting Dispatcher")
        # Open a Zmq PULL socket to the Dispatcher (ZMQ Streamer Device)
        try:
            context = zmq.Context()
            consumer_receiver = context.socket(zmq.PULL)
            consumer_receiver.RCVTIMEO = 1000  # 1 second recv timeout
            consumer_receiver.connect("tcp://dispatcher:5560")
        except Exception:
            print("[E] Error contacting Dispatcher. Exiting.")
            sys.exit(5)
        print("[*] Dispatcher ONLINE.\n")

        i = 0
        print("[*] Initial Worker Pong.")
        self.worker_pong()
        print("[*] Entering main loop.")
        while True:
            # print("Executor: Message #{:4}".format(i))
            try:
                workSpec = consumer_receiver.recv_json()
            except zmq.Again:
                self.worker_pong()
                continue
            except Exception:
                print("[E] Exception at recv_json()")
                return(False)

            i += 1

            if workSpec['action'] in ExecutorCore.VALID_ACTIONS:
                action = workSpec['action']
            else:
                print("Executor: INVALID ACTION RECEIVED. Exiting.")
                return(False)

            if action == 'ping':
                self.worker_pong()
            elif action == 'queue_jobs':
                # Tag us alive before and after plugin run
                self.worker_pong()
                self.run_plugins(workSpec=workSpec)
                self.worker_pong()  # TODO: check if this is better

            if i >= 1000:
                return(True)
        return(False)


if __name__ == "__main__":
    print("This file is not to be called directly.")
