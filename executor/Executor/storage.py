#!/usr/bin/env python3

import sys
import json
import redis
import datetime
from pprint import pprint

""" The Storage class implements all code that interacts against REDIS.
"""


class Storage():
    ONE_YEAR = 31556952

    @classmethod
    def RedisDB(cls, decode_responses=True):
        return(redis.StrictRedis(host="redis", port=6379, db=0,
                                 decode_responses=decode_responses))

    @classmethod
    def register_plugin(cls, plugin_name=None):
        if plugin_name is None:
            return(None)
        rdb = cls.RedisDB()
        ret = rdb.sadd("PLUGINNAME_SET", plugin_name)
        cls.snapshot()
        return(ret)

    @classmethod
    # TODO: decide if we must check if any data is stored, also
    def key_exists(cls, key):
        # print("Checking for key existance [ {} ]".format(key))
        rdb = cls.RedisDB()
        ret = rdb.exists(key)
        # print("EXISTANCE = {}".format(ret))
        return(rdb.exists(key))

    @classmethod
    def get_asset(cls, assetId):
        rdb = cls.RedisDB()
        key = 'ASSET_{}'.format(assetId)
        ret = rdb.get(key)  # None for nonexistant key
        return(ret)

    @classmethod
    def snapshot(cls):
        rdb = cls.RedisDB()
        rdb.save()

    @classmethod
    def get_stats_by_plugin_and_assetId(cls, plugin_name=None, assetId=None):
        rdb = cls.RedisDB()
        key = "STATS_{}_{}".format(assetId, plugin_name)
        if not rdb.exists(key):
            return(None)

    @classmethod
    def store_results_key_list(cls, plugin_name=None, assetId=None, key=None):
        # Step 1, validate
        if plugin_name is None:
            return(None)
        if assetId is None:
            return(None)
        if key is None:
            return(None)
        # Step 2, append
        wkey = "STATS_{}_{}".format(assetId, plugin_name)
        rdb = cls.RedisDB()
        ret = rdb.rpush(wkey, key)

    @classmethod
    def store_results_hash(cls, key=None, results=None):
        # Step 1, validate
        if key is None:
            return(None)
        if results is None:
            return(None)
        # Step 2, store results in redis Hash
        rdb = cls.RedisDB()
        ret = rdb.hmset(key, results)
        ret = rdb.expire(key, cls.ONE_YEAR)
        # Step 3, store results['RESULT'] to STATS_{ID}
        # holds latest results from all plugins for {ID}.
        # Valid values are pluginName:OK/WARNING/ERROR

    @classmethod
    def update_latest_result(cls, assetId=None, plugin_name=None,
                             result=None):
        # Step 1, validate
        if assetId is None:
            return(None)
        if plugin_name is None:
            return(None)
        if result is None:
            return(None)
        # Step 2, update hash field plugin_name on STATS_{ID}
        # using result value
        rdb = cls.RedisDB()
        key = "STATS_{}".format(assetId)
        ret = rdb.hset(key, plugin_name, result)

    @classmethod
    def retrieve_old_results(cls, assetId=None, plugin_name=None, count=None):
        # Step 1, validate
        if assetId is None:
            return(None)
        if plugin_name is None:
            return(None)
        if count is None:
            return(None)
        # Step 2, use lrange on the key
        key = "STATS_{}_{}".format(assetId, plugin_name)
        rdb = cls.RedisDB()
        keys = rdb.lrange(key, -(int(count)), -1)
        # print("storage.retrieve_old_results()")
        # pprint(keys)
        results = []
        for resultKey in keys:
            result = rdb.hgetall(resultKey)
            results.append(result)
        if len(results) == 0:
            return(None)
        else:
            return(results)

    @classmethod
    def worker_name_taken(cls, name=None):
        if name is None:
            return(None)
        key = "WORKER_PING_SCORE"
        rdb = cls.RedisDB()
        ret = rdb.zscore(key, name)
        if ret is None:
            return(False)
        else:
            return(True)

    @classmethod
    def worker_name_set(cls, name=None):
        if name is None:
            return(None)
        ret = cls.worker_reset_score(name=name)
        return(ret)

    @classmethod
    def worker_reset_score(cls, name=None):
        if name is None:
            return(None)
        key = "WORKER_PING_SCORE"
        rdb = cls.RedisDB()
        ret = rdb.zadd(key, 0, name)
        return(ret)

    @classmethod
    def append_asset_notification(cls, assetId=None,
                                  plugin_name=None,
                                  datestring=None,
                                  data=None):
        if assetId is None:
            return(None)
        if plugin_name is None:
            return(None)
        if data is None:
            return(None)
        if datestring is None:
            return(None)
        # We will use our itemName as name for the hash key that
        # will store data TODO: document on master key index document
        datakey = "NOTIFICATION_DATAHASH_{}_{}_{}".format(assetId,
                                                          datestring,
                                                          plugin_name)
        dsetkey = "NOTIFICATION_{}".format(assetId,)
        expDate = datetime.timedelta(days=365)
        dset = DeadSet(keyname=dsetkey, default_expire=expDate)
        dset.add_expiring_item(itemId=datakey)
        rdb = cls.RedisDB()
        data['datestring'] = datestring
        data['fulldate'] = float(datetime.datetime.utcnow().timestamp())
        print(data['fulldate'])
        data['plugin'] = plugin_name
        # pprint(data)
        ret = rdb.hmset(datakey, data)
        ret = rdb.expire(datakey, expDate)
        cls.snapshot()
        msg = "created {} expiring item/key on {}".format(datakey, dsetkey)
        print(msg)
        return(ret)


class DeadSet():
    def __init__(self, keyname=None, default_expire=None, rdb=None):
        # TODO: validate kwargs
        self.keyname = keyname
        if type(default_expire) is datetime.timedelta:
            self.default_expire = default_expire
        else:
            raise ValueError
        if rdb is None:
            self.redis = redis.StrictRedis(host="redis", port=6379, db=0,
                                           decode_responses=True)
        else:
            if not str(type(rdb)).startswith("<class 'redis.client."):
                raise TypeError
            else:
                self.redis = rdb

    def expire_date_as_score(self):
        future = datetime.datetime.utcnow() + self.default_expire
        return(future.timestamp())

    def add_expiring_item(self, itemId=None):
        if itemId is None:
            return(None)
        rdb = self.redis
        print("DEADSET: adding {} to {}".format(itemId, self.keyname))
        ret = rdb.zadd(self.keyname, self.expire_date_as_score(), itemId)
        return(ret)

    def expire_items(self):
        timestamp = datetime.datetime.utcnow().timestamp()
        ret = self.redis.zremrangebyscore(self.keyname,
                                          0,
                                          timestamp)
        return(ret)

    def zscan(self):
        return(self.redis.zscan(self.keyname))
