import numpy
import requests
import socket
import lxml

from pprint import pprint
from bs4 import BeautifulSoup as BS

from Executor.plugin_api import PluginApi
from Executor.plugin import ExecutorPlugin
# TODO: define Plugin API (run(), stats(), cleanup()?)
# TODO: implement the actual HtmlStats plugin


class HtmlStats(ExecutorPlugin):
    author = 'Arturo Busleiman <buanzo@buanzo.com.ar>'
    description = 'Applies stddev to html tags for threshold determination'
    default = True

    def __init__(self):
        self.name = self.__class__.__name__
        self.api = PluginApi(callerName=self.name)

    # for plugins, I avoid using __init__ for setup.
    def setup(self, datestring=None, workername=None, cmd=None):
        if datestring is None or cmd is None:
            return(None)
        else:
            self.datestring = datestring
            self.cmd = cmd
        self.api.set_datestring(self.datestring)
        # print("{} : setup(datestring={},cmd={})".format(self.name,
        #                                                 self.datestring,
        #                                                 self.cmd,))
        if workername is None:
            return(None)
        else:
            self.workername = workername
            self.api.set_workername(name=workername)
    # In the future, many jobs can be run at once per datestring
    # hence the separation between setup() and run()

    def run(self, work=None):
        if work is None:
            return(None)
        aId = work['asset_id']
        aUrl = work['asset_url']
        # plugin_api.get_key_name_by_assetId also sets
        # the .key variable on the plugin_api class instance
        self.key = self.api.get_key_name_by_assetId(assetId=aId)
        # print("{} : keyname = {}".format(self.name, self.key))
        if self.api.key_exists(self.key):
            # print("{} : key exists. we are late.".format(self.name,
            #                                              self.key))
            return(None)
        self.api.pong()
        htc,http_status = self.count_html_tags(url=aUrl)  # Html Tag Count
        self.api.pong()
        # print("{} : html_tag_count({}) = {}".format(self.name,
        #                                             aUrl,
        #                                             htc,))
        results = {}
        results['tag_count'] = htc
        results['http_status'] = http_status

        try:
            prev = self.api.retrieve_old_results(count=1)  # TODO: baseline settings
            old_result = prev[0]
        except Exception:  # No previous result
            prev = None
            results['RESULT'] = self.api.RESULT_OK
            old_result = {'tag_count': htc}

        previous_htc = old_result['tag_count']

        try:
            if 'tag_count' in prev:
                results['prev_tag_count'] = prev['tag_count']
            if 'http_status' in prev:
                results['prev_http_status'] = prev['http_status']
        except:
            pass

        # Apply numpy standard deviation:
        ret = numpy.std([int(previous_htc), int(htc)])
        results['std_dev'] = ret
        if ret < 10:
            results['RESULT'] = self.api.RESULT_OK
        elif ret < 25:
            results['RESULT'] = self.api.RESULT_WARNING
        else:
            results['RESULT'] = self.api.RESULT_ERROR
        # Now store the info
        self.api.store_new_results(results=results)
        # See if a notification (readable stats) must happen
        self.api.act_on_results(cur=results, prev=prev)
        # print("Done. run() exiting.\n")

    def count_html_tags(self, url):
        # print("About to request {} with timeout=60".format(url))
        socket.setdefaulttimeout(60)
        try:
            resp = requests.get(url, timeout=60)
            html = resp.text
        except Exception:
            print("Exception htc:requests.get()")
            return(0,None)  # Yes, because we get zero html tags
        # print("About to soup")
        soup = BS(html, 'lxml')
        # print("About to run len(soup.find_all())")
        return(len(soup.find_all()),resp.status_code)
