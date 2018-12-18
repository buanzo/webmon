#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

from flask_restful import Resource, request
from ronald.storage import Storage


class API_Workers(Resource):
    def __init__(self):
        """
        Class Initialization.
        """
        pass

    def get(self, assetId=None):
        return(Storage.get_worker_status())

    def delete(self, assetId=None):
        """
        DELETE method handler for API_Workers
        """
        pass


if __name__ == '__main__':
    print("")
