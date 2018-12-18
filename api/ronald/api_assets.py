#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>

import redis
from ronald.errors import *
from ronald.storage import Storage, Asset
from flask_restful import Resource, request, abort as restAbort
from pprint import pprint


class API_Assets(Resource):
    def __init__(self):
        """
        Class Initialization.
        Assets API uses the Storage class, which is a redis abstraction
        """
        pass

    def get(self, assetId=None):
        """
        GET method handler for API_Assets
        """
        if assetId is None:
            assets = Storage.list_assets()
            return(assets)
        else:
            return(Asset(assetId=assetId).get())

    def delete(self, assetId=None):
        """
        DELETE method handler for API_Assets
        """
        if assetId is None:
            abort(400, message=ERR_MSG_ASSETS_DELETE_NO_ASSETID)
        return(Asset(assetId=assetId).delete())

    def put(self, assetId=None):
        """
        PUT method handler for API_Assets
        """
        if assetId is not None:
            restAbort(400, message=ERR_MSG_ASSETS_PUT_NO_ARGS_REQ)
        # get parameters
        js = request.get_json(force=True)
        # validate
        if 'assetUrl' not in js:
            restAbort(400, message=ERR_MSG_ASSETS_PUT_INVALID_REQUEST)
        # TODO: check if assetUrl is indeed a valid Url
        # attempt to create new asset
        newAsset = Asset(assetUrl=js['assetUrl']).create()
        # Asset() always returns a dictionary. send to client.
        return(newAsset)


if __name__ == '__main__':
    print("")
