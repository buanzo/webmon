import imp
import os

from pprint import pprint


class ExecutorPluginBase(type):
    plugins = []

    def __init__(cls, name, bases, attrs):
        if name != 'ExecutorPlugin':
            ExecutorPluginBase.plugins.append(cls)

    @classmethod
    def prettyPrint(cls):
        print("+{:-<19}+{:-<56}+".format('', ''))
        print("| {:^17} | {:^54} |".format("Plugin Name", "Description"))
        print("+{:-<19}+{:-<56}+".format('', ''))
        for plugin in ExecutorPluginBase.plugins:
            n = plugin.__name__
            d = plugin.description
            if plugin.default:
                n = '{}*'.format(n)
            print("| {:17} | {:54} |".format(n, d))
        print("+{:-<19}+{:-<56}+".format('', ''))
        print("Note: A plugin marked with * runs by default.\n")


class ExecutorPlugin(object, metaclass=ExecutorPluginBase):
    author = 'Arturo Busleiman <buanzo@buanzo.com.ar>'
    description = 'ExecutorPlugin is the class Plugins will base on'
    default = False

    def __init__(self, name=None, default=False):
        self.name = name


def load_plugins():
    dirs = ['{}/Executor/plugins/'.format(os.getcwd())]
    for dir in dirs:
        for filename in os.listdir(dir):
            modname, ext = os.path.splitext(filename)
            if ext == '.py':
                file, path, descr = imp.find_module(modname, [dir])
                if file:
                    mod = imp.load_module(modname, file, path, descr)
    return ExecutorPluginBase.plugins
