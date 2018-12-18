#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Arturo 'Buanzo' Busleiman

import os
import sys
from pathlib import Path

from Executor.core import ExecutorCore
from Executor.storage import Storage

from pprint import pprint


class PluginApi():
    RESULT_OK = 0
    RESULT_WARNING = 1
    RESULT_ERROR = 2

    def __init__(self, callerName=None):
        if callerName is None:
            # Pyblack magic to get caller name out of ModuleSpec
            # We will issue a status message so the operator
            # can tell which plugin is lacking the parameter
            # I might remove this black magic code
            for f in sys._current_frames().values():
                x = f.f_back.f_globals['__spec__']
                self.callerName = str(x).split('name=')[1] \
                                        .split(',')[0] \
                                        .replace("'", "")
                # self.report_status('PluginApi lacks callerName parameter')
                del f
                del x
                break
        else:
            self.callerName = callerName
        self.key = None
        self.register()
        print("Plugin {} initialized.".format(self.callerName))

    def set_datestring(self, datestring):
        self.datestring = datestring

    def set_workername(self, name):
        self.workername = name

    def register(self):
        Storage.register_plugin(plugin_name=self.callerName)

    def pong(self):
        # A plugin might need to tell the system it is alive
        Storage.worker_reset_score(name=self.workername)

    def key_exists(self, key):
        return(Storage.key_exists(key))

    def get_key_name_by_assetId(self, assetId=None):
        if assetId is None:
            return(None)
        key = "STATS_{}_{}_{}".format(assetId,
                                      self.callerName,
                                      self.datestring)
        self.key = key
        self.assetId = assetId
        return(key)

    def get_stats_key_name_by_assetId(self, assetId=None):
        if assetId is None:
            return(None)
        key = "STATS_{}_{}".format(assetId,
                                   self.callerName)
        return(key)

    """ The plugin_key_read and plugin_key_write methods
    allow a plugin to use the RedisDB for particular storage
    reasons. The actual key name is built using:
    PLUGIN_PARTICULAR_{PLUGINNAME}_{NAME}.
    PLUGINNAME is self.callerName.
    NAME is indicated via kwargs by plugins. """
    def plugin_key_read(self, name=None, type=None):
        # TODO: plugin_key_read and plugin_key_write
        # validate name
        # validate type {hash, string, list, integer?}
        # desired type vs actual type
        # use: https://redis.io/commands/type for further validation
        pass

    def plugin_key_write(self, name=None, type=None):
        pass

    """ Each plugin will store_results.
    The results kwarg must be a dictionary of non-nested structures
    example: {'somekey': somevalue, 'anotherkey': anothervalue}.
    This way, the information can be stored on a Redis Hash.

    The function is named store_NEW_results, to further clarify
    the fact that plugins can obtain OLD results, for statistical
    purposes or whatnot.

    Only one value will be stored on the "latest results from all
    plugins" key (STATS_{ID}). That value needs to have the
    special dictionary key name "RESULT". The value can only be
    one of 0 (OK), 1 (WARNING), 2 (ERROR)

    TODO: everything, and also this needs to populate the statskey
    STATS_{ID}_{PLUGINNAME} """
    def store_new_results(self, results=None):
        # Step one, validate
        if self.key is None:
            return(None)  # self.get_key_name_by_assetId() not called?
        if results is None:
            return(None)
        # Step two, check if key already exists
        if self.key_exists(self.key):
            return(None)  # we are too late?
        # Step three, add self.key to STATS_{ID}_{PLUGINNAME} redis list
        Storage.store_results_key_list(plugin_name=self.callerName,
                                       assetId=self.assetId,
                                       key=self.key)
        # Step four, store results hash to the appropiate key
        # STATS_{ID}_{PLUGINNAME}_{DATE} (self.key)
        Storage.store_results_hash(key=self.key, results=results)
        # Step five, store results['RESULT'] to STATS_{ID}
        # which is a redish hash. fieldname = plugin_name
        # value = results['RESULT']
        Storage.update_latest_result(assetId=self.assetId,
                                     plugin_name=self.callerName,
                                     result=results['RESULT'])
        Storage.snapshot()

    """ A plugin can obtain the 'count' (kwarg default 10)
    old results, for statistical purposes and whatnot.
    'count' values above 100 are not accepted.
    """
    def retrieve_old_results(self, count=10):
        ret = Storage.retrieve_old_results(assetId=self.assetId,
                                           plugin_name=self.callerName,
                                           count=count)
        return(ret)

    def act_on_results(self, cur=None, prev=None):
        notify = False
        # print("ACT_ON_RESULTS(cur={}, prev={})".format(cur,prev))
        if cur is None:  # should not happen
            return(None)
        if prev is None:  # might be first run
            notify = True
        else:
            prev = prev[len(prev)-1]

        if notify is False:
            a = int(cur['RESULT'])
            b = int(prev['RESULT'])
            if int(cur['RESULT']) != int(prev['RESULT']):
                print("Change. Will notify.")
                notify = True

        if notify is True:
            pn = self.callerName
            ret = Storage.append_asset_notification(assetId=self.assetId,
                                                    plugin_name=pn,
                                                    datestring=self.datestring,
                                                    data=cur)
        return(notify)
