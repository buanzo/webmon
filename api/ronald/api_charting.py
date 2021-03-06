#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

from flask_restful import Resource, request
from ronald.storage import Storage


class API_Charting(Resource):
    def __init__(self):
        """
        Class Initialization.
        """
        pass

    def get(self, count=None, assetId=False):
        if count == 'all':
            self.count = -1  # Standard, use -1 to specify 'all'
        elif count == 'latest':
            self.count = 10  # TODO: define from config
        else:
            try:
                self.count = int(count)
            except Exception:
                return({'status': 'ERROR',
                        'detail': 'Invalid count parameter'})
            if self.count < 1:
                return({'status': 'ERROR',
                        'detail': 'Count parameter must be > 0'})

        print("self.count={} assetId={}".format(self.count, assetId))
        if assetId is False:
            pass
            # return(Storage.get_chartdata(library='default',count=self.count))

        if Storage.get_asset(assetId=assetId) is None:
            return({'status': 'ERROR',
                    'detail': 'Invalid or inexistent asset'})

        # return(Storage.get_chartdata(library='default',count=self.count,
        #                              assetId=))


if __name__ == '__main__':
    print("")
