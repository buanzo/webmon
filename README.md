Web Monitoring
--------------

Webmon executes plugins against assets (URLs, originally).

The API will contain groups of calls, divided in asset management,
statistics gathering and execution.

Asset Management involves URL management, adding, modifying and removing
items (i.e "https://somesite.net, http://some.other.server/somespecificURI,
etc").

Statistics Gathering will provide statistical information about said assets.

Execution will provide the necessary means to push jobs to the work queue.

Storage is implemented in Redis


Work Queue
----------

The Jobs API (A Ronald Class) will send jobs to a Messaging Queue (zeromq). 
This Queue will be read by the Dispatcher, which is a standalone module. 


Statistics
----------

The statistics API will provide information about assets. Information will
come from the different plugins that the Executor enables. All plugins will
be executed for each Asset.


Executor Module (standalone)
----------------------------

The Executor Module will be a Task Worker, using the standard zeromq
Streamer: http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/devices/streamer.html

Dispatcher Module (standalone)
------------------------------

The Dispatcher Module will act as a broker. The Jobs API class will use zeromq
to communicate with the Dispatcher, indicating Job IDs.

Protocols
---------

Each executor will have access to all plugins, directly, hence no need to do
unsafe things like transporting code. The executor is NOT a generic 'worker'
node. The transport between Jobs API <-> Dispatcher <-> Executor is zeromq.

The transport between Executor and Storage is Redis.


TO DO LIST
----------

In consideration to https://redis.io/topics/persistence, snapshots will be
triggered after each important API call, and whenever the Dispatcher gets a
"SNAPSHOT NOW" command over its zeromq control channel.

The AOF (Append-Only-File) is a persistence method for
Redis Key-Value noSQL storage system). It is comparable to a Changelog.

The RDB (Redis Database) is the snapshot-style persistence method. This is
what we will be using.

https://www.fullstackpython.com/blog/install-redis-use-python-3-ubuntu-1604.html

https://redis.io/commands/save

https://redis.io/commands/bgsave

PLUGINS
-------

* HtmlStats: uses numpy to create standard deviation statistical
  calculations to detect excessive changes between different parameters such
  as html tags, pagesize in bytes, etc.

There are other plugins included.
