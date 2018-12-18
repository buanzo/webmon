#!/usr/bin/env python3

import sys
import json
import redis
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
    def worker_increment_score(cls, name=None):
        if name is None:
            return(None)
        rdb = cls.RedisDB()
        key = "WORKER_PING_SCORE"
        if not rdb.exists(key):
            return(None)
        ret = rdb.zincrby(key, name, 1)
        return(ret)

    @classmethod
    def get_worker_status(cls):
        rdb = cls.RedisDB()
        key = "WORKER_PING_SCORE"
        ret = rdb.zscan(key)
        return(ret)

    @classmethod
    def worker_purge(cls, score=300):
        rdb = cls.RedisDB()
        ret = rdb.zremrangebyscore("WORKER_PING_SCORE", score, 'inf')
        return(ret)

    @classmethod
    def get_latest_datestring(cls):
        rdb = cls.RedisDB()
        ret = rdb.get("LATEST_DATESTRING")
        return(ret)


if __name__ == '__main__':
    pass
