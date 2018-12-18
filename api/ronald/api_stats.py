#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

from flask_restful import Resource, request
from ronald.storage import Storage, AssetStats


class API_Stats(Resource):
    def __init__(self):
        """
        Class Initialization.
        """
        pass

    def get(self, assetId=None):
        """
        GET method handler for API_Stats
        This method returns the stored statistics
        for a specific assetId, or a list of
        available statistics for all assets.
        """
        stats = AssetStats(assetId=assetId).get()
        return(stats)

    def post(self, assetId=None):
        """
        POST method is the full-stats version of GET
        """
        stats = AssetStats(assetId=assetId).get(full=True)
        return(stats)

    def delete(self, assetId=None):  # TODO: get datapoint from Request
        """
        DELETE method handler for API_Stats
        """
        pass


if __name__ == '__main__':
    print("")
