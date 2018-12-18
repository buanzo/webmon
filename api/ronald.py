#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo Busleiman <buanzo@buanzo.com.ar>


from flask import Flask, request
from flask_restful import Api, Resource

"""This is a comment.
   Yes. Very nice.
"""

from ronald.api_assets import API_Assets
from ronald.api_stats import API_Stats
from ronald.api_jobs import API_Jobs
from ronald.api_workers import API_Workers
from ronald.api_notifications import API_Notifications
from ronald.api_charting import API_Charting

#
# INITIALIZATION
#
ronald_app = Flask(__name__)
api = Api(ronald_app)

#
# API Routing
#

api.add_resource(API_Assets,
                 '/assets',
                 '/assets/',
                 '/assets/<assetId>',
                 )

api.add_resource(API_Stats,
                 '/stats',
                 '/stats/',
                 '/stats/<assetId>',
                 )

api.add_resource(API_Jobs,
                 '/jobs',
                 '/jobs/',
                 '/jobs/<jobId>',
                 )

api.add_resource(API_Workers,
                 '/workers',
                 '/workers/',
                 )

api.add_resource(API_Notifications,
                 '/notifications',
                 '/notifications/',
                 '/notifications/<count>',
                 '/notifications/<count>/<assetId>',
                 )

api.add_resource(API_Charting,
                 '/charting',
                 '/charting/',
                 '/charting/<count>',
                 '/charting/<count>/<assetId>',
                 )

if __name__ == '__main__':
    ronald_app.run(host='0.0.0.0', debug=True)
    # Remember to cleanup here [dbClose(), etc, etc]
