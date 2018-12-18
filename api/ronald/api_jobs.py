#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

import zmq
import time
from ronald.storage import Storage
from ronald.messaging import Messaging
from flask_restful import Resource, request
from pprint import pprint

""" The API_Jobs class implements job management.
    get() _might_ list upcoming jobs. (redis?)
    delete() cancels a job
    put() inserts a job
    post(), if implemented, will allow to modify
    an existing job's parameters
"""


class API_Jobs(Resource):
    def __init__(self):
        """
        Class Initialization.
        """
        pass

    def get(self, jobId=None):
        """
        GET method handler for API_Jobs.
        Takes care of getting a list of assets that need
        to be run at the current period, and sending that
        list to the Dispatcher, via ZMQ (implemented in Messaging class)
        """
        workSpec = Storage.list_assets_without_current_stats()
        # pprint(workSpec)
        ret = Messaging.queue_jobs(workSpec=workSpec)
        if workSpec['assets'] is None:
            return({'status': 'ERROR',
                    'detail': 'No available workers. Notify admin.'})
        return({'status': 'OK',
                'detail': 'Jobs have been pushed to workers',
                'dispatched_work_specification': workSpec})

    def post(self, jobId=None):
        """
        POST method handler for API_Jobs
        """
        pass

    def delete(self, jobId=None):
        """
        DELETE method handler for API_Jobs
        """
        pass

    def put(self, jobId=None):
        """
        PUT method handler for API_Jobs
        """
        pass


if __name__ == '__main__':
    print("")
