#!/usr/bin/env python3

import zmq
import json
import sys
from pprint import pprint


""" This class implements API-side and
utility methods for ZMQ Messaging.
It is used by api_jobs.py
"""


class Messaging():
    def __init__(self):
        pass

    @classmethod
    def queue_jobs(cls, workSpec=None):
        if workSpec is None:
            return(None)
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.connect("tcp://dispatcher:5559")
        work = {}
        if workSpec['assets'] is None or len(workSpec['assets']) == 0:
            return(None)
        else:
            work['action'] = 'queue_jobs'
        work['data'] = workSpec['assets']
        work['datestring'] = workSpec['datestring']
        zmq_socket.send_json(work)
        zmq_socket.disconnect("tcp://dispatcher:5559")
