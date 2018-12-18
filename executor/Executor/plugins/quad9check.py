import numpy
import requests
import socket
import lxml
import dns.resolver

from pprint import pprint
from urllib.parse import urlparse
from Executor.plugin_api import PluginApi
from Executor.plugin import ExecutorPlugin
# TODO: define Plugin API (run(), stats(), cleanup()?)
# TODO: implement the actual HtmlStats plugin


class Quad9check(ExecutorPlugin):
    author = "Arturo Busleiman <buanzo@buanzo.com.ar>"
    description = "Checks an asset's hostname against quad9's dns service"
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
        try:
            aId = work['asset_id']
            aDomain = urlparse(work['asset_url']).netloc
        except Exception:
            return(None)

        self.key = self.api.get_key_name_by_assetId(assetId=aId)
        if self.api.key_exists(self.key):
            return(None)
        self.api.pong()
        flagged = self.quad9test(fqdn=aDomain)  # quad9 NXDOMAIN for fqdn?
        self.api.pong()
        # print("{} : html_tag_count({}) = {}".format(self.name,
        #                                             aUrl,
        #                                             htc,))
        results = {}
        results['quad9_flagged'] = flagged

        try:
            prev = self.api.retrieve_old_results(count=1)
            old_result = prev[0]
        except Exception:  # No previous result
            prev = None
            results['RESULT'] = self.api.RESULT_OK
            old_result = {'quad9_flagged': False }

        previous_flagged = old_result['quad9_flagged']

        try:
            if 'quad9_flagged' in prev:
                results['prev_quad9_flagged'] = prev['prev_quad9_flagged']
        except:
            pass

        if flagged:
            results['RESULT'] = self.api.RESULT_ERROR
        else:
            results['RESULT'] = self.api.RESULT_OK

        # Now store the info
        self.api.store_new_results(results=results)
        # See if a notification (readable stats) must happen
        self.api.act_on_results(cur=results, prev=prev)

    def quad9test(self,fqdn=None):
        if fqdn is None:
            return(None)
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = ['9.9.9.9','2620:fe::fe']
        try:
            r = dns.resolver.query(fqdn, 'a')
        except dns.resolver.NXDOMAIN:
            return(True)
        return(False)
