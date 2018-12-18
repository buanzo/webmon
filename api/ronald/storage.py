#!/usr/bin/env python3

import redis
import json
import sys
from random import shuffle
from pprint import pprint
from datetime import datetime
from pprint import pprint

""" The Storage class implements all code that interacts against REDIS.
It is important to understand the different Redis data types, and
what operations are NOT O(1) [i.e FAST].

Lists allow for duplicate values, hence we will use that data type
to store statistical data fed by plugins.

Sets DO NOT allow duplicate values, so they are useful for IDs.

To create an asset id, we have a COUNTER_ASSET_ID key that we INCRement.

Then, the ID will be pushed to the ASSET_IDS key using SET data.

This way we do not need to get all the keys, then filter out the ASSET_{ID}
ones to get a list of Asset IDs.

Useful URLs:
https://redis.io/commands/sadd
https://redis.io/topics/data-types-intro
https://redis.io/commands#set
https://redis.io/commands#list
"""


class Storage():
    @classmethod
    def RedisDB(cls, decode_responses=True):
        return(redis.StrictRedis(host="redis", port=6379, db=0,
                                 decode_responses=decode_responses))

    @classmethod
    def get_unused_assetId(cls):
        rdb = cls.RedisDB(decode_responses=False)
        ret_id = rdb.incr("COUNTER_ASSET_ID")
        cls.snapshot()
        ret_set = rdb.sismember("ASSET_ID_SET", ret_id)
        if ret_set is True:  # This should NOT happen
            return(None)
        return(ret_id)

    @classmethod
    def get_assetId_by_url(cls, assetUrl=None):
        if assetUrl is None:
            return(None)
        rdb = cls.RedisDB()
        key = "URL_{}".format(assetUrl)
        ret = rdb.get(key)
        return(ret)

    @classmethod
    def list_assets(cls, fulldata=True):
        rdb = cls.RedisDB()
        len = rdb.scard("ASSET_ID_SET")
        asset_ids = rdb.smembers("ASSET_ID_SET")
        assets = []
        if fulldata is True:
            for aId in list(asset_ids):
                asset = {}
                ret = cls.get_asset(aId)
                asset['asset_id'] = aId
                asset['asset_url'] = ret
                assets.append(asset)
        else:
            assets = list(asset_ids)
        retObj = {}
        retObj['assets'] = assets
        retObj['len_assets'] = len
        return(retObj)

    @classmethod
    def list_plugin_names(cls):
        rdb = cls.RedisDB()
        len = rdb.scard("PLUGINNAME_SET")
        plugin_names = rdb.smembers("PLUGINNAME_SET")
        return(list(plugin_names))

    @classmethod
    def get_asset(cls, assetId):
        rdb = cls.RedisDB()
        key = 'ASSET_{}'.format(assetId)
        ret = rdb.get(key)  # None for nonexistant key
        return(ret)

    @classmethod
    def create_asset(cls, assetUrl=None):
        ret = cls.get_assetId_by_url(assetUrl=assetUrl)
        if ret is not None:  # if the asset already exists
            return(ret)
        newId = cls.get_unused_assetId()
        if newId is None:
            return(None)
        key = 'ASSET_{}'.format(newId)
        rdb = cls.RedisDB()
        ret = rdb.sadd("ASSET_ID_SET", newId)
        ret = rdb.set(key, assetUrl)
        key = 'URL_{}'.format(assetUrl)
        ret = rdb.set(key, newId)
        cls.snapshot()
        return(newId)

    @classmethod
    def delete_asset(cls, assetId, assetUrl):  # TODO: delete stats?
        rdb = cls.RedisDB()
        key = 'ASSET_{}'.format(assetId)
        ret = rdb.delete(key)
        key = 'URL_{}'.format(assetUrl)
        ret = rdb.delete(key)
        ret = rdb.srem("ASSET_ID_SET", assetId)
        cls.snapshot()
        if ret == 0:
            return(None)
        return(True)

    @classmethod
    def set_latest_datestring(cls, ds=None):
        if ds is None:
            return(None)
        rdb = cls.RedisDB()
        key = 'LATEST_DATESTRING'
        ret = rdb.set(key, ds)
        # cls.snapshot()
        return(ret)

    @classmethod
    def list_assets_without_current_stats(cls):  # TODO FIX
        # TODO: create date string: YYYYMMDDHH
        # the code below will return similar to: '2017110812'
        rdb = cls.RedisDB()
        now = datetime.now()
        ds = '{:04d}{:02d}{:02d}{:02d}{:02d}'.format(now.year,
                                                     now.month,
                                                     now.day,
                                                     now.hour,
                                                     now.minute)
        cls.set_latest_datestring(ds=ds)
        # for each asset, for each plugin name, check if key exists
        assets = cls.list_assets()['assets']
        # pprint(assets)

        plugin_names = cls.list_plugin_names()
        # pprint(plugin_names)

        assets_to_run = []
        # Redis supports from 3.0.3 multiple-keys for the EXISTS command
        # but it only returns a number, and not the key names
        dup_check = []
        for asset in assets:
            aId = asset['asset_id']
            for pName in plugin_names:
                key = "STATS_{}_{}_{}".format(aId, pName, ds,)
                if aId not in dup_check and rdb.exists(key)==False:
                    # print("NO SUCH KEY {}".format(key))
                    dup_check.append(aId)  # TODO: add some sort of lock()
                    assets_to_run.append(asset)  # TODO: limit to plugin+id?
        # print("ASSETS_TO_RUN:")
        # pprint(assets_to_run)
        # print("DUP_CHECK:")
        # pprint(dup_check)
        workSpec = {}
        workSpec['datestring'] = ds
        shuffle(assets_to_run)
        # print("ASSETS_TO_RUN POST SHUFFLE:")
        # pprint(assets_to_run)
        nWorkers = cls.get_worker_count(score=5)
        # print("NWORKERS = {}".format(nWorkers))
        if nWorkers == 0:  # TODO: fix
            workSpec['assets'] = None
        else:
            slice = len(assets_to_run) / nWorkers
            # print("SLICE = {} ".format(int(slice)))
            workSpec['assets'] = assets_to_run[:int(slice)]
        workSpec['available_workers'] = nWorkers
        return(workSpec)

    @classmethod
    def snapshot(cls):
        rdb = cls.RedisDB()
        rdb.save()

    @classmethod
    def get_worker_count(cls, score=None):
        rdb = cls.RedisDB()
        key = "WORKER_PING_SCORE"
        if not rdb.exists(key):
            return(0)
        else:
            if score is not None:
                return(rdb.zcount(key, 0, score))
            else:
                return(zdb.zcard(key))

    @classmethod
    def get_worker_status(cls):
        rdb = cls.RedisDB()
        key = "WORKER_PING_SCORE"
        ret = rdb.zscan(key)
        return(ret)

    @classmethod
    def retrieve_asset_stats(cls, assetId=None):
        rdb = cls.RedisDB()
        retObj = {}
        if assetId is None:  # client wants stats for all assets
            retObj['status'] = 'ERROR'
            retObj['detail'] = 'Not implemented'
            assets = Storage.list_assets()['assets']  # TODO: check len_assets
            data = []
            for asset in assets:
                obj = {}
                # pprint(asset)
                obj['asset_id'] = asset['asset_id']
                obj['asset_url'] = asset['asset_url']
                obj['asset_stats_url'] = '/stats/{}'.format(asset['asset_id'])
                data.append(obj)
            retObj['data'] = data
            return(retObj)

        key = 'STATS_{}'.format(assetId)
        if not rdb.exists(key):
            retObj['status'] = 'ERROR'
            retObj['detail'] = 'Asset has no statistics'
        else:
            retObj['status'] = 'OK'
            retObj['detail'] = 'Latest stats for AssetId#{}'.format(assetId)
            retObj['data'] = {'plugin_status': rdb.hgetall(key),
                              'asset_url': rdb.get('ASSET_{}'.format(assetId)),
                              'asset_id': assetId}
        return(retObj)

    @classmethod
    def get_notifications(cls, count=None, assetId=None):
        #  return({'count': count, 'assetId': assetId})
        if assetId is None:
            assets_to_check = Storage.list_assets(fulldata=False)['assets']
        else:
            assets_to_check = [assetId]
        keyFmt = "NOTIFICATION_{}"
        r = cls.RedisDB()
        retObj = {}  # For returning to Flask
        timedata = {}  # all of our notifications
        for asset in assets_to_check:
            key = keyFmt.format(asset)
            for item in r.zscan(key)[1]:
                datakey = item[0]
                data = r.hgetall(datakey)
                aId = str(item).split('_')[2]
                aUrl = Storage.get_asset(assetId=aId)
                data['asset_id'] = aId
                data['asset_url'] = aUrl
                ds = float(data['fulldate'])
                timedata[ds] = data
        dates = []
        for ds in reversed(sorted(timedata.keys())):
            ds = float(ds)
            dates.append(timedata[ds])
        retObj['status'] = "OK"
        retObj['detail'] = "Notifications"
        if count == -1:
            retObj['data'] = dates
        else:
            retObj['data'] = dates[0:int(count)]
        retObj['len_data'] = len(retObj['data'])
        return(retObj)


""" This class represents a webmon Asset, with useful
attributes and methods. Helps create a new Asset,
as well as obtaining an existing one.
Check api_assets.py for more information.

It is important to note that an Asset object does not
include any kind of statistical information, including
time since last check, etc.

That kind of information is only accesible through
the Statistics API.
"""


class Asset():
    def __init__(self, assetId=None, assetUrl=None):
        if assetUrl is None:
            self.assetUrl = Storage.get_asset(assetId)
        else:
            self.assetUrl = assetUrl
        self.assetId = assetId

    def create(self):
        if self.assetUrl is None:
            retObj = {}
            retObj['status'] = 'error'
            retObj['detail'] = 'asking to create, but no assetUrl provided'
            return(retObj)
        ret = Storage.create_asset(assetUrl=self.assetUrl)
        if ret is None:  # We couldnt create asset. no id.
            retObj = {}
            retObj['status'] = 'error'
            retObj['detail'] = 'could not create asset. no id returned.'
            return(retObj)
        else:
            self.assetId = ret
        ret = self.get()
        return(ret)

    def get(self):
        ret = Storage.get_asset(assetId=self.assetId)
        if ret is None:
            retObj = {}
            retObj['status'] = 'error'
            retObj['detail'] = 'asset not found.'
            return(retObj)
        else:  # success
            retObj = {}
            retObj['status'] = 'OK'
            retObj['assetId'] = self.assetId
            retObj['assetUrl'] = ret
            retObj['api_asset_url'] = "/assets/{}".format(self.assetId)
            return(retObj)

    def delete(self):
        ret = Storage.delete_asset(assetId=self.assetId,
                                   assetUrl=self.assetUrl)
        if ret is None:
            retObj = {}
            retObj['status'] = 'error'
            retObj['detail'] = 'cannot delete asset.'
            return(retObj)
        else:  # success
            retObj = {}
            retObj['status'] = 'OK'
            retObj['assetId'] = self.assetId
            retObj['detail'] = 'asset deleted'
            return(retObj)


""" This class represents a Job object. It is used
by both the Jobs and Stats APIs, as well as other
backend software such as Workers.
TODO: everything
"""


class Job():
    def __init__(self):
        pass


""" This class represents the Statistics of an Asset.
It will contain utility methods such as needs_checking(),
submit(), etc.

It probably is a good idea to implement .expire() for certain
stats keys.
"""


class AssetStats():
    def __init__(self, assetId=None):
        self.stats = Storage.retrieve_asset_stats(assetId=assetId)

    def get(self, full=False):
        if not full:  # GET on /stats/<assetId>
            return(self.stats)
        # POST on /stats/<assetId> triggers full=True
